"""Create initial admin user if none exists.

Usage: ADMIN_PASSWORD=<senha> python seed_admin.py
"""
import os
import sys

password = os.environ.get("ADMIN_PASSWORD")
if not password:
    print("Set ADMIN_PASSWORD env var before running this script.")
    sys.exit(1)

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
        u.set_senha(password)
        db.session.add(u)
        db.session.commit()
        print("Admin created successfully")
