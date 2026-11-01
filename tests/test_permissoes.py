import uuid

from app.extensions import db
from app.models.empresa import Empresa
from tests.conftest import login


def test_gestor_dono_acessa_gestores(client, usuario_gestor_dono):
    login(client, "dono@test.com")
    resp = client.get("/gestor/gestores")
    assert resp.status_code == 200


def test_gestor_nao_acessa_gestores(client, usuario_gestor):
    login(client, "gestor@test.com")
    resp = client.get("/gestor/gestores")
    assert resp.status_code == 403


def test_cliente_nao_acessa_clientes_gestor(client, usuario_cliente):
    login(client, "cliente@test.com")
    resp = client.get("/gestor/clientes")
    assert resp.status_code == 403


def test_cliente_nao_acessa_leads_outra_empresa(
    client, app, usuario_cliente, empresa_fixture
):
    outra_empresa = Empresa(
        id=uuid.uuid4(),
        nome="Outra Empresa",
        gestor_id=empresa_fixture[1].id,
    )
    db.session.add(outra_empresa)
    db.session.commit()

    login(client, "cliente@test.com")
    resp = client.get(f"/leads/{outra_empresa.id}")
    assert resp.status_code == 403


def test_gestor_nao_acessa_empresa_outro_gestor(
    client, app, usuario_gestor, empresa_fixture
):
    outro_gestor = __import__("app.models.usuario", fromlist=["Usuario"]).Usuario(
        id=uuid.uuid4(),
        email="outro_gestor@test.com",
        nome="Outro Gestor",
        perfil="gestor",
        status="ativo",
    )
    outro_gestor.set_senha("senha123")
    db.session.add(outro_gestor)
    db.session.flush()

    outra_empresa = Empresa(
        id=uuid.uuid4(),
        nome="Empresa Outro Gestor",
        gestor_id=outro_gestor.id,
    )
    db.session.add(outra_empresa)
    db.session.commit()

    login(client, "gestor@test.com")
    resp = client.get(f"/gestor/clientes/{outra_empresa.id}")
    assert resp.status_code == 403


def test_unauthenticated_redirected(client):
    resp = client.get("/gestor/clientes")
    assert resp.status_code == 302
    assert "/login" in resp.headers.get("Location", "")
