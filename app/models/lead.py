import uuid
from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db

VALID_TRANSITIONS = {
    "novo": ["orcamento", "perdido"],
    "orcamento": ["contrato", "perdido", "novo"],
    "contrato": [],
    "perdido": [],
}


class Lead(db.Model):
    __tablename__ = "lead"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("empresa.id"), nullable=False
    )
    nome = db.Column(db.String(200), nullable=True)
    telefone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    origem_campanha = db.Column(db.String(300), nullable=True)
    origem_conjunto = db.Column(db.String(300), nullable=True)
    origem_anuncio = db.Column(db.String(300), nullable=True)
    status = db.Column(
        db.Enum("novo", "orcamento", "contrato", "perdido", name="status_lead_enum"),
        nullable=False,
        default="novo",
    )
    valor_contrato = db.Column(db.Numeric(12, 2), nullable=True)
    criado_em = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    atualizado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    empresa = db.relationship("Empresa", back_populates="leads")

    __table_args__ = (
        db.Index("ix_lead_empresa_status", "empresa_id", "status"),
        db.Index("ix_lead_empresa_criado", "empresa_id", "criado_em"),
    )

    def pode_transicionar_para(self, novo_status):
        return novo_status in VALID_TRANSITIONS.get(self.status, [])

    def __repr__(self):
        return f"<Lead {self.nome} status={self.status}>"
