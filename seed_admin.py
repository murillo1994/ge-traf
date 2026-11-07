"""Create initial admin user if none exists."""
import os

os.environ.setdefault("FLASK_CONFIG", "production")

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario

app = create_app(os.environ.get("FLASK_CONFIG", "production"))

with app.app_context():
    u = Usuario.query.filter_by(email="admin@getraf.com").first()
    if u:
        print("Admin already exists")
    else:
        u = Usuario(
            email="admin@getraf.com",
            nome="Admin",
            perfil="gestor_dono",
            status="ativo",
        )
        u.set_senha("admin123")
        db.session.add(u)
        db.session.commit()
        print("Admin created successfully")
