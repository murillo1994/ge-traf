import logging
from datetime import UTC, date, datetime, timedelta

from app.extensions import db
from app.models.conta_anuncio import ContaAnuncio
from app.models.empresa import Empresa
from app.models.metrica_diaria import MetricaDiaria
from app.services.crypto import decrypt_token
from app.services.meta_ads import get_insights

logger = logging.getLogger(__name__)


def sync_empresa(empresa_id):
    empresa = Empresa.query.get(empresa_id)
    if not empresa:
        logger.error("Empresa %s não encontrada", empresa_id)
        return

    conta = ContaAnuncio.query.filter_by(
        empresa_id=empresa_id, plataforma="meta", status="ativo"
    ).first()
    if not conta:
        logger.info("Empresa %s sem conta Meta ativa", empresa_id)
        return

    try:
        access_token = decrypt_token(conta.token_criptografado)
    except Exception:
        logger.exception("Erro ao descriptografar token da empresa %s", empresa_id)
        empresa.status_conexao = "reconexao_necessaria"
        conta.status = "expirado"
        db.session.commit()
        return

    date_end = date.today().isoformat()
    date_start = (date.today() - timedelta(days=1)).isoformat()

    try:
        insights = get_insights(
            access_token, conta.conta_id_externo, date_start, date_end
        )
    except Exception:
        logger.exception("Erro ao buscar insights da empresa %s", empresa_id)
        empresa.status_conexao = "reconexao_necessaria"
        conta.status = "expirado"
        db.session.commit()
        return

    count = 0
    for row in insights:
        existing = MetricaDiaria.query.filter_by(
            empresa_id=empresa_id,
            data=date.today(),
            anuncio_id=row["ad_id"],
        ).first()

        if existing:
            existing.impressoes = row["impressions"]
            existing.cliques = row["clicks"]
            existing.gasto = row["spend"]
            existing.leads_gerados = row["leads"]
            existing.sincronizado_em = datetime.now(UTC)
        else:
            metrica = MetricaDiaria(
                empresa_id=empresa_id,
                conta_anuncio_id=conta.id,
                data=date.today(),
                campanha_id=row["campaign_id"],
                campanha_nome=row["campaign_name"],
                conjunto_id=row.get("adset_id"),
                conjunto_nome=row.get("adset_name"),
                anuncio_id=row["ad_id"],
                anuncio_nome=row["ad_name"],
                impressoes=row["impressions"],
                cliques=row["clicks"],
                gasto=row["spend"],
                leads_gerados=row["leads"],
            )
            db.session.add(metrica)
        count += 1

    db.session.commit()
    logger.info("Empresa %s: %d métricas sincronizadas", empresa_id, count)


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
