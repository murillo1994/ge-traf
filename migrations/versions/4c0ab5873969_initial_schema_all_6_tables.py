"""initial schema - all 6 tables

Revision ID: 4c0ab5873969
Revises:
Create Date: 2026-11-01 11:29:10.043122

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4c0ab5873969"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create usuario first (no FK to empresa yet)
    op.create_table(
        "usuario",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column(
            "perfil",
            sa.Enum("gestor_dono", "gestor", "cliente", name="perfil_enum"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("pendente", "ativo", "inativo", name="status_usuario_enum"),
            nullable=False,
        ),
        sa.Column("empresa_id", sa.Uuid(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # 2. Create empresa (FK to usuario.id is safe now)
    op.create_table(
        "empresa",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.Column("segmento", sa.String(length=100), nullable=True),
        sa.Column(
            "teto_verba_mensal", sa.Numeric(precision=12, scale=2), nullable=True
        ),
        sa.Column("gestor_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status_conexao",
            sa.Enum(
                "aguardando",
                "conectado",
                "reconexao_necessaria",
                name="status_conexao_enum",
            ),
            nullable=False,
        ),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["gestor_id"], ["usuario.id"], name="fk_empresa_gestor"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 3. Add the circular FK: usuario.empresa_id -> empresa.id
    op.create_foreign_key(
        "fk_usuario_empresa", "usuario", "empresa", ["empresa_id"], ["id"]
    )

    # 4. Create remaining tables
    op.create_table(
        "conta_anuncio",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column(
            "plataforma",
            sa.Enum("meta", "google", name="plataforma_enum"),
            nullable=False,
        ),
        sa.Column("conta_id_externo", sa.String(length=100), nullable=False),
        sa.Column("token_criptografado", sa.LargeBinary(), nullable=False),
        sa.Column("token_expira_em", sa.DateTime(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("ativo", "expirado", "revogado", name="status_conta_enum"),
            nullable=False,
        ),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresa.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "plataforma", name="uq_empresa_plataforma"),
    )

    op.create_table(
        "lead",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=200), nullable=True),
        sa.Column("telefone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("origem_campanha", sa.String(length=300), nullable=True),
        sa.Column("origem_conjunto", sa.String(length=300), nullable=True),
        sa.Column("origem_anuncio", sa.String(length=300), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "novo", "orcamento", "contrato", "perdido", name="status_lead_enum"
            ),
            nullable=False,
        ),
        sa.Column("valor_contrato", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresa.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lead_empresa_criado", "lead", ["empresa_id", "criado_em"])
    op.create_index("ix_lead_empresa_status", "lead", ["empresa_id", "status"])

    op.create_table(
        "log_auditoria",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("acao", sa.String(length=100), nullable=False),
        sa.Column("entidade_tipo", sa.String(length=50), nullable=False),
        sa.Column("entidade_id", sa.Uuid(), nullable=False),
        sa.Column("dados_anteriores", sa.JSON(), nullable=True),
        sa.Column("dados_novos", sa.JSON(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresa.id"],
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuario.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_log_auditoria_empresa_criado", "log_auditoria", ["empresa_id", "criado_em"]
    )

    op.create_table(
        "metrica_diaria",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("conta_anuncio_id", sa.Uuid(), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("campanha_id", sa.String(length=100), nullable=False),
        sa.Column("campanha_nome", sa.String(length=300), nullable=False),
        sa.Column("conjunto_id", sa.String(length=100), nullable=True),
        sa.Column("conjunto_nome", sa.String(length=300), nullable=True),
        sa.Column("anuncio_id", sa.String(length=100), nullable=True),
        sa.Column("anuncio_nome", sa.String(length=300), nullable=True),
        sa.Column("impressoes", sa.Integer(), nullable=False),
        sa.Column("cliques", sa.Integer(), nullable=False),
        sa.Column("gasto", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("leads_gerados", sa.Integer(), nullable=False),
        sa.Column("criativo_url", sa.String(length=500), nullable=True),
        sa.Column("criativo_titulo", sa.String(length=300), nullable=True),
        sa.Column("sincronizado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["conta_anuncio_id"],
            ["conta_anuncio.id"],
        ),
        sa.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresa.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "empresa_id", "data", "anuncio_id", name="uq_metrica_empresa_data_anuncio"
        ),
    )
    op.create_index("ix_metrica_empresa_data", "metrica_diaria", ["empresa_id", "data"])


def downgrade():
    op.drop_index("ix_metrica_empresa_data", table_name="metrica_diaria")
    op.drop_table("metrica_diaria")
    op.drop_index("ix_log_auditoria_empresa_criado", table_name="log_auditoria")
    op.drop_table("log_auditoria")
    op.drop_index("ix_lead_empresa_status", table_name="lead")
    op.drop_index("ix_lead_empresa_criado", table_name="lead")
    op.drop_table("lead")
    op.drop_table("conta_anuncio")
    op.drop_foreign_key("fk_usuario_empresa", "usuario")
    op.drop_table("empresa")
    op.drop_table("usuario")
