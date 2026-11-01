import uuid
from datetime import UTC, datetime

import bcrypt
from flask_login import UserMixin
from sqlalchemy import Uuid

from app.extensions import db, login_manager


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    id = db.Column(Uuid, primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    perfil = db.Column(
        db.Enum("gestor_dono", "gestor", "cliente", name="perfil_enum"),
        nullable=False,
    )
    status = db.Column(
        db.Enum("pendente", "ativo", "inativo", name="status_usuario_enum"),
        nullable=False,
        default="pendente",
    )
    empresa_id = db.Column(Uuid, db.ForeignKey("empresa.id"), nullable=True)
    criado_em = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    atualizado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    empresa = db.relationship(
        "Empresa", foreign_keys=[empresa_id], back_populates="usuarios"
    )

    def set_senha(self, plain):
        self.senha_hash = bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    def check_senha(self, plain):
        return bcrypt.checkpw(plain.encode(), self.senha_hash.encode())

    def __repr__(self):
        return f"<Usuario {self.email}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, uuid.UUID(user_id))
