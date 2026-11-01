from tests.conftest import login


def test_login_success(client, usuario_gestor_dono):
    resp = login(client, "dono@test.com")
    assert resp.status_code == 200


def test_login_wrong_password(client, usuario_gestor_dono):
    resp = client.post("/login", data={"email": "dono@test.com", "senha": "errada"})
    assert b"incorretos" in resp.data


def test_logout_redirect(client, usuario_gestor_dono):
    login(client, "dono@test.com")
    resp = client.get("/logout", follow_redirects=True)
    assert b"Entrar" in resp.data


def test_registro_creates_pendente(client, app):
    resp = client.post(
        "/registro",
        data={
            "nome": "Novo Gestor",
            "email": "novo@test.com",
            "senha": "senha12345",
            "confirmar_senha": "senha12345",
        },
        follow_redirects=True,
    )
    assert b"Aguarde" in resp.data

    from app.models.usuario import Usuario

    with app.app_context():
        u = Usuario.query.filter_by(email="novo@test.com").first()
        assert u is not None
        assert u.status == "pendente"
        assert u.perfil == "gestor"


def test_registro_duplicate_email(client, usuario_gestor_dono):
    resp = client.post(
        "/registro",
        data={
            "nome": "Duplicado",
            "email": "dono@test.com",
            "senha": "senha12345",
            "confirmar_senha": "senha12345",
        },
        follow_redirects=True,
    )
    assert b"cadastrado" in resp.data
