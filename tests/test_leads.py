import uuid

from app.extensions import db
from app.models.lead import Lead
from app.models.log_auditoria import LogAuditoria
from tests.conftest import login


def _create_lead(empresa_id, status="novo"):
    lead = Lead(
        id=uuid.uuid4(),
        empresa_id=empresa_id,
        nome="Lead Teste",
        telefone="11999999999",
        origem_campanha="Campanha Teste",
        status=status,
    )
    db.session.add(lead)
    db.session.commit()
    return lead


def test_transition_novo_to_orcamento(client, usuario_gestor, empresa_fixture):
    empresa, gestor = empresa_fixture
    lead = _create_lead(empresa.id)

    login(client, gestor.email)
    resp = client.post(
        f"/leads/{lead.id}/status",
        data={
            "novo_status": "orcamento",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    db.session.refresh(lead)
    assert lead.status == "orcamento"


def test_orcamento_to_contrato_requires_valor(client, usuario_gestor, empresa_fixture):
    empresa, gestor = empresa_fixture
    lead = _create_lead(empresa.id, status="orcamento")

    login(client, gestor.email)
    resp = client.post(
        f"/leads/{lead.id}/status",
        data={
            "novo_status": "contrato",
        },
        follow_redirects=True,
    )
    assert b"obrigat" in resp.data

    db.session.refresh(lead)
    assert lead.status == "orcamento"


def test_orcamento_to_contrato_with_valor(client, usuario_gestor, empresa_fixture):
    empresa, gestor = empresa_fixture
    lead = _create_lead(empresa.id, status="orcamento")

    login(client, gestor.email)
    resp = client.post(
        f"/leads/{lead.id}/status",
        data={
            "novo_status": "contrato",
            "valor_contrato": "3500.00",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    db.session.refresh(lead)
    assert lead.status == "contrato"
    assert float(lead.valor_contrato) == 3500.00


def test_invalid_transition_contrato_to_novo(client, usuario_gestor, empresa_fixture):
    empresa, gestor = empresa_fixture
    lead = _create_lead(empresa.id, status="contrato")
    lead.valor_contrato = 1000
    db.session.commit()

    login(client, gestor.email)
    resp = client.post(
        f"/leads/{lead.id}/status",
        data={
            "novo_status": "novo",
        },
        follow_redirects=True,
    )
    assert b"permitida" in resp.data

    db.session.refresh(lead)
    assert lead.status == "contrato"


def test_status_change_creates_audit_log(client, app, usuario_gestor, empresa_fixture):
    empresa, gestor = empresa_fixture
    lead = _create_lead(empresa.id)

    login(client, gestor.email)
    client.post(
        f"/leads/{lead.id}/status",
        data={
            "novo_status": "orcamento",
        },
        follow_redirects=True,
    )

    log = LogAuditoria.query.filter_by(
        entidade_tipo="lead",
        entidade_id=lead.id,
    ).first()
    assert log is not None
    assert log.acao == "lead_status_alterado"
    assert log.dados_anteriores["status"] == "novo"
    assert log.dados_novos["status"] == "orcamento"


def test_cliente_only_sees_own_leads(client, usuario_cliente, empresa_fixture):
    _empresa, gestor = empresa_fixture
    from app.models.empresa import Empresa

    outra_empresa = Empresa(
        id=uuid.uuid4(),
        nome="Outra",
        gestor_id=gestor.id,
    )
    db.session.add(outra_empresa)
    db.session.commit()

    login(client, "cliente@test.com")
    resp = client.get(f"/leads/{outra_empresa.id}")
    assert resp.status_code == 403


def test_gestor_only_sees_assigned_leads(client, empresa_fixture):
    _empresa, gestor = empresa_fixture
    from app.models.empresa import Empresa
    from app.models.usuario import Usuario

    outro_gestor = Usuario(
        id=uuid.uuid4(),
        email="outro2@test.com",
        nome="Outro",
        perfil="gestor",
        status="ativo",
    )
    outro_gestor.set_senha("senha123")
    db.session.add(outro_gestor)
    db.session.flush()

    outra_empresa = Empresa(
        id=uuid.uuid4(),
        nome="Outra",
        gestor_id=outro_gestor.id,
    )
    db.session.add(outra_empresa)
    db.session.commit()

    login(client, gestor.email)
    resp = client.get(f"/leads/{outra_empresa.id}")
    assert resp.status_code == 403
