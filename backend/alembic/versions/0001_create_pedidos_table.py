"""create pedidos table

Revision ID: 0001
Revises:
Create Date: 2026-03-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pedidos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="processing"),
        sa.Column("pedido_pdf_key", sa.Text, nullable=True),
        sa.Column("relatorio_pdf_key", sa.Text, nullable=True),
        sa.Column("template_excel_key", sa.Text, nullable=True),
        sa.Column("resultado_excel_key", sa.Text, nullable=True),
        sa.Column("resumo", postgresql.JSONB, nullable=True),
        sa.Column("results", postgresql.JSONB, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("processing_time_seconds", sa.Float, nullable=True),
    )
    op.create_index("ix_pedidos_created_at", "pedidos", ["created_at"])
    op.create_index("ix_pedidos_status", "pedidos", ["status"])


def downgrade() -> None:
    op.drop_index("ix_pedidos_status", "pedidos")
    op.drop_index("ix_pedidos_created_at", "pedidos")
    op.drop_table("pedidos")
