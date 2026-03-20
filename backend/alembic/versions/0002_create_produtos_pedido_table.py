"""create produtos_pedido table

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "produtos_pedido",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "pedido_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pedidos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Dados do template Excel (planilha de produtos da fábrica)
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("descricao", sa.Text, nullable=False, server_default=""),
        sa.Column("tamanho_embalagem", sa.Integer, nullable=False, server_default="0"),
        sa.Column("linha_template", sa.Integer, nullable=True),
        # Quantidades
        sa.Column("qp", sa.Integer, nullable=False, server_default="0"),   # quantidade pedida
        sa.Column("qa", sa.Integer, nullable=False, server_default="0"),   # quantidade adicional
        sa.Column("total", sa.Integer, nullable=False, server_default="0"), # qp + qa
        # Recebimento via XML NF-e
        sa.Column("qtd_recebida", sa.Integer, nullable=True),
        # Status do item
        sa.Column("status", sa.String(30), nullable=False, server_default="ok"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_produtos_pedido_pedido_id", "produtos_pedido", ["pedido_id"])
    op.create_index("ix_produtos_pedido_codigo", "produtos_pedido", ["codigo"])


def downgrade() -> None:
    op.drop_index("ix_produtos_pedido_codigo", "produtos_pedido")
    op.drop_index("ix_produtos_pedido_pedido_id", "produtos_pedido")
    op.drop_table("produtos_pedido")
