import uuid
from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db


class MetricaDiaria(db.Model):
    __tablename__ = "metrica_diaria"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("empresa.id"), nullable=False
    )
    conta_anuncio_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("conta_anuncio.id"), nullable=False
    )
    data = db.Column(db.Date, nullable=False)
    campanha_id = db.Column(db.String(100), nullable=False)
    campanha_nome = db.Column(db.String(300), nullable=False)
    conjunto_id = db.Column(db.String(100), nullable=True)
    conjunto_nome = db.Column(db.String(300), nullable=True)
    anuncio_id = db.Column(db.String(100), nullable=True)
    anuncio_nome = db.Column(db.String(300), nullable=True)
    impressoes = db.Column(db.Integer, nullable=False, default=0)
    cliques = db.Column(db.Integer, nullable=False, default=0)
    gasto = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    leads_gerados = db.Column(db.Integer, nullable=False, default=0)
    criativo_url = db.Column(db.String(500), nullable=True)
    criativo_titulo = db.Column(db.String(300), nullable=True)
    sincronizado_em = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )

    conta_anuncio = db.relationship("ContaAnuncio")
    empresa = db.relationship("Empresa")

    __table_args__ = (
        db.UniqueConstraint(
            "empresa_id", "data", "anuncio_id", name="uq_metrica_empresa_data_anuncio"
        ),
        db.Index("ix_metrica_empresa_data", "empresa_id", "data"),
    )

    def __repr__(self):
        return f"<MetricaDiaria {self.data} empresa={self.empresa_id}>"
