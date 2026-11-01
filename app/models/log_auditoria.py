import uuid
from datetime import UTC, datetime

from sqlalchemy import Uuid

from app.extensions import db


class LogAuditoria(db.Model):
    __tablename__ = "log_auditoria"

    id = db.Column(Uuid, primary_key=True, default=uuid.uuid4)
    empresa_id = db.Column(Uuid, db.ForeignKey("empresa.id"), nullable=False)
    usuario_id = db.Column(Uuid, db.ForeignKey("usuario.id"), nullable=False)
    acao = db.Column(db.String(100), nullable=False)
    entidade_tipo = db.Column(db.String(50), nullable=False)
    entidade_id = db.Column(Uuid, nullable=False)
    dados_anteriores = db.Column(db.JSON, nullable=True)
    dados_novos = db.Column(db.JSON, nullable=True)
    criado_em = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )

    usuario = db.relationship("Usuario")
    empresa = db.relationship("Empresa")

    __table_args__ = (
        db.Index("ix_log_auditoria_empresa_criado", "empresa_id", "criado_em"),
    )

    def __repr__(self):
        return f"<LogAuditoria {self.acao} {self.entidade_tipo}>"
