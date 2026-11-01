import uuid

import pytest
from cryptography.fernet import Fernet

from app import create_app
from app.extensions import db as _db
from app.models.empresa import Empresa
from app.models.usuario import Usuario


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    app.config["FERNET_KEY"] = Fernet.generate_key().decode()
    from app.extensions import init_fernet

    with app.app_context():
        init_fernet(app.config["FERNET_KEY"])
    yield app


@pytest.fixture(autouse=True)
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def empresa_fixture(db):
    gestor = Usuario(
        id=uuid.uuid4(),
        email="gestor@test.com",
        nome="Gestor Teste",
        perfil="gestor",
        status="ativo",
    )
    gestor.set_senha("senha123")
    db.session.add(gestor)
    db.session.flush()

    empresa = Empresa(
        id=uuid.uuid4(),
        nome="Fotografia Eventos",
        segmento="Fotografia",
        teto_verba_mensal=5000,
        gestor_id=gestor.id,
    )
    db.session.add(empresa)
    db.session.commit()
    return empresa, gestor


@pytest.fixture
def usuario_gestor_dono(db):
    u = Usuario(
        id=uuid.uuid4(),
        email="dono@test.com",
        nome="Dono Teste",
        perfil="gestor_dono",
        status="ativo",
    )
    u.set_senha("senha123")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def usuario_gestor(empresa_fixture):
    _, gestor = empresa_fixture
    return gestor


@pytest.fixture
def usuario_cliente(db, empresa_fixture):
    empresa, _ = empresa_fixture
    u = Usuario(
        id=uuid.uuid4(),
        email="cliente@test.com",
        nome="Cliente Teste",
        perfil="cliente",
        status="ativo",
        empresa_id=empresa.id,
    )
    u.set_senha("senha123")
    db.session.add(u)
    db.session.commit()
    return u


def login(client, email, senha="senha123"):
    return client.post(
        "/login", data={"email": email, "senha": senha}, follow_redirects=True
    )
