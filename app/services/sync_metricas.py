import logging
from datetime import UTC, date, datetime, timedelta

from app.extensions import db
from app.models.conta_anuncio import ContaAnuncio
from app.models.empresa import Empresa
from app.models.metrica_diaria import MetricaDiaria
from app.services.crypto import decrypt_token

logger = logging.getLogger(__name__)


def _sync_conta(empresa, conta):
    try:
        access_token = decrypt_token(conta.token_criptografado)
    except Exception:
        logger.exception("Erro ao descriptografar token da conta %s", conta.id)
        conta.status = "expirado"
        db.session.commit()
        return 0

    date_end = date.today().isoformat()
    date_start = (date.today() - timedelta(days=1)).isoformat()

    if conta.plataforma == "meta":
        from app.services.meta_ads import get_insights

        try:
            insights = get_insights(access_token, conta.conta_id_externo, date_start, date_end)
        except Exception:
            logger.exception("Erro Meta insights empresa %s", empresa.id)
            conta.status = "expirado"
            db.session.commit()
            return 0

    elif conta.plataforma == "google":
        from app.services.google_ads import get_insights, refresh_access_token

        if conta.refresh_token_criptografado:
            try:
                refresh_token = decrypt_token(conta.refresh_token_criptografado)
                access_token = refresh_access_token(refresh_token)
            except Exception:
                logger.exception("Erro ao renovar token Google empresa %s", empresa.id)
                conta.status = "expirado"
                db.session.commit()
                return 0

        try:
            insights = get_insights(access_token, conta.conta_id_externo, date_start, date_end)
        except Exception:
            logger.exception("Erro Google insights empresa %s", empresa.id)
            conta.status = "expirado"
            db.session.commit()
            return 0
    else:
        return 0

    count = 0
    for row in insights:
        ad_id = row["ad_id"] or f"{conta.plataforma}_{row['campaign_id']}"
        existing = MetricaDiaria.query.filter_by(
            empresa_id=empresa.id,
            data=date.today(),
            anuncio_id=ad_id,
        ).first()

        if existing:
            existing.impressoes = row["impressions"]
            existing.cliques = row["clicks"]
            existing.gasto = row["spend"]
            existing.leads_gerados = row["leads"]
            existing.sincronizado_em = datetime.now(UTC)
        else:
            metrica = MetricaDiaria(
                empresa_id=empresa.id,
                conta_anuncio_id=conta.id,
                data=date.today(),
                campanha_id=row["campaign_id"],
                campanha_nome=row["campaign_name"],
                conjunto_id=row.get("adset_id"),
                conjunto_nome=row.get("adset_name"),
                anuncio_id=ad_id,
                anuncio_nome=row["ad_name"],
                impressoes=row["impressions"],
                cliques=row["clicks"],
                gasto=row["spend"],
                leads_gerados=row["leads"],
            )
            db.session.add(metrica)
        count += 1

    db.session.commit()
    return count


def sync_empresa(empresa_id):
    empresa = Empresa.query.get(empresa_id)
    if not empresa:
        logger.error("Empresa %s não encontrada", empresa_id)
        return

    contas = ContaAnuncio.query.filter_by(
        empresa_id=empresa_id, status="ativo"
    ).all()

    if not contas:
        logger.info("Empresa %s sem contas ativas", empresa_id)
        return

    total = 0
    alguma_falhou = False
    for conta in contas:
        count = _sync_conta(empresa, conta)
        if count == 0 and conta.status == "expirado":
            alguma_falhou = True
        total += count

    if alguma_falhou and not any(c.status == "ativo" for c in contas):
        empresa.status_conexao = "reconexao_necessaria"
        db.session.commit()

    logger.info("Empresa %s: %d métricas sincronizadas (%d contas)", empresa_id, total, len(contas))


def sync_todas():
    empresas = Empresa.query.filter_by(status_conexao="conectado").all()
    logger.info("Iniciando sincronização para %d empresas", len(empresas))

    for empresa in empresas:
        try:
            sync_empresa(empresa.id)
        except Exception:
            logger.exception("Erro não tratado ao sincronizar empresa %s", empresa.id)
            continue

    logger.info("Sincronização concluída")
