import uuid
from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db


class ContaAnuncio(db.Model):
    __tablename__ = "conta_anuncio"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("empresa.id"), nullable=False
    )
    plataforma = db.Column(
        db.Enum("meta", "google", name="plataforma_enum"),
        nullable=False,
    )
    conta_id_externo = db.Column(db.String(100), nullable=False)
    token_criptografado = db.Column(db.LargeBinary, nullable=False)
    token_expira_em = db.Column(db.DateTime, nullable=True)
    status = db.Column(
        db.Enum("ativo", "expirado", "revogado", name="status_conta_enum"),
        nullable=False,
        default="ativo",
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

    empresa = db.relationship("Empresa", back_populates="contas")

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "plataforma", name="uq_empresa_plataforma"),
    )

    def __repr__(self):
        return f"<ContaAnuncio {self.plataforma} empresa={self.empresa_id}>"
