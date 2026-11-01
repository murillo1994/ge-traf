import uuid
from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db


class Empresa(db.Model):
    __tablename__ = "empresa"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = db.Column(db.String(200), nullable=False)
    segmento = db.Column(db.String(100), nullable=True)
    teto_verba_mensal = db.Column(db.Numeric(12, 2), nullable=True)
    gestor_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("usuario.id"), nullable=False
    )
    status_conexao = db.Column(
        db.Enum(
            "aguardando",
            "conectado",
            "reconexao_necessaria",
            name="status_conexao_enum",
        ),
        nullable=False,
        default="aguardando",
    )
    criado_em = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    atualizado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    gestor = db.relationship("Usuario", foreign_keys=[gestor_id])
    usuarios = db.relationship(
        "Usuario", foreign_keys="Usuario.empresa_id", back_populates="empresa"
    )
    contas = db.relationship("ContaAnuncio", back_populates="empresa", lazy="dynamic")
    leads = db.relationship("Lead", back_populates="empresa", lazy="dynamic")

    def __repr__(self):
        return f"<Empresa {self.nome}>"
