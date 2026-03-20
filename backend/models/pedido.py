import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from db.session import Base


def utcnow():
    return datetime.now(timezone.utc)


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    status = Column(String(20), nullable=False, default="processing")
    # processing | completed | failed

    # Chaves GCS
    pedido_pdf_key = Column(Text, nullable=True)
    relatorio_pdf_key = Column(Text, nullable=True)
    template_excel_key = Column(Text, nullable=True)
    resultado_excel_key = Column(Text, nullable=True)

    # Resultado
    resumo = Column(JSONB, nullable=True)
    results = Column(JSONB, nullable=True)

    # Diagnóstico
    error_message = Column(Text, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)

    # Relacionamento com itens do pedido
    produtos = relationship("ProdutoPedido", back_populates="pedido", cascade="all, delete-orphan")
