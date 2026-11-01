import uuid
from unittest.mock import patch

from app.extensions import db
from app.models.conta_anuncio import ContaAnuncio
from app.models.empresa import Empresa
from app.models.metrica_diaria import MetricaDiaria
from app.models.usuario import Usuario
from app.services.crypto import encrypt_token


def _setup_empresa_with_conta(db_session):
    gestor = Usuario(
        id=uuid.uuid4(),
        email="sync_gestor@test.com",
        nome="Sync Gestor",
        perfil="gestor",
        status="ativo",
    )
    gestor.set_senha("senha123")
    db_session.add(gestor)
    db_session.flush()

    empresa = Empresa(
        id=uuid.uuid4(),
        nome="Empresa Sync",
        gestor_id=gestor.id,
        status_conexao="conectado",
    )
    db_session.add(empresa)
    db_session.flush()

    token = encrypt_token("fake-access-token")
    conta = ContaAnuncio(
        id=uuid.uuid4(),
        empresa_id=empresa.id,
        plataforma="meta",
        conta_id_externo="123456",
        token_criptografado=token,
    )
    db_session.add(conta)
    db_session.commit()
    return empresa, conta


MOCK_INSIGHTS = [
    {
        "campaign_id": "c1",
        "campaign_name": "Campanha 1",
        "adset_id": "as1",
        "adset_name": "Conjunto 1",
        "ad_id": "ad1",
        "ad_name": "Anúncio 1",
        "impressions": 1000,
        "clicks": 50,
        "spend": 150.00,
        "leads": 5,
    },
    {
        "campaign_id": "c1",
        "campaign_name": "Campanha 1",
        "adset_id": "as1",
        "adset_name": "Conjunto 1",
        "ad_id": "ad2",
        "ad_name": "Anúncio 2",
        "impressions": 2000,
        "clicks": 100,
        "spend": 300.00,
        "leads": 10,
    },
]


def test_sync_empresa_creates_metricas(app):
    with app.app_context():
        empresa, _conta = _setup_empresa_with_conta(db.session)

        with patch(
            "app.services.sync_metricas.get_insights", return_value=MOCK_INSIGHTS
        ):
            from app.services.sync_metricas import sync_empresa

            sync_empresa(empresa.id)

        count = MetricaDiaria.query.filter_by(empresa_id=empresa.id).count()
        assert count == 2


def test_sync_expired_token_marks_reconexao(app):
    with app.app_context():
        empresa, _conta = _setup_empresa_with_conta(db.session)

        with patch(
            "app.services.sync_metricas.decrypt_token",
            side_effect=Exception("bad token"),
        ):
            from app.services.sync_metricas import sync_empresa

            sync_empresa(empresa.id)

        db.session.refresh(empresa)
        assert empresa.status_conexao == "reconexao_necessaria"


def test_sync_upsert_no_duplicates(app):
    with app.app_context():
        empresa, _conta = _setup_empresa_with_conta(db.session)

        with patch(
            "app.services.sync_metricas.get_insights", return_value=MOCK_INSIGHTS
        ):
            from app.services.sync_metricas import sync_empresa

            sync_empresa(empresa.id)
            sync_empresa(empresa.id)

        count = MetricaDiaria.query.filter_by(empresa_id=empresa.id).count()
        assert count == 2
