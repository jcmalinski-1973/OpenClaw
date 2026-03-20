import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.session import Base


def utcnow():
    return datetime.now(timezone.utc)


class ProdutoPedido(Base):
    __tablename__ = "produtos_pedido"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pedido_id = Column(UUID(as_uuid=True), ForeignKey("pedidos.id", ondelete="CASCADE"), nullable=False, index=True)

    # Dados do template Excel (planilha de produtos da fábrica)
    codigo = Column(String(50), nullable=False)          # col 1 – código do produto
    descricao = Column(Text, nullable=False, default="") # col 2 – descrição
    tamanho_embalagem = Column(Integer, nullable=False, default=0)  # col 3 – pack_size
    linha_template = Column(Integer, nullable=True)      # linha na planilha

    # Quantidades
    qp = Column(Integer, nullable=False, default=0)      # quantidade pedida (suggested_packs do PDF)
    qa = Column(Integer, nullable=False, default=0)      # quantidade adicional calculada
    total = Column(Integer, nullable=False, default=0)   # qp + qa

    # Recebimento (preenchido ao importar XML da NF-e)
    qtd_recebida = Column(Integer, nullable=True)        # quantidade recebida conforme NF-e

    # Status do item no processamento
    status = Column(String(30), nullable=False, default="ok")
    # ok | template_not_found | stock_not_found

    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relacionamento reverso (opcional, para queries ORM)
    pedido = relationship("Pedido", back_populates="produtos")
