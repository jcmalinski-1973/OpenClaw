from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel


class PedidoResumo(BaseModel):
    order_items_found: int = 0
    processed_ok: int = 0
    template_not_found: int = 0
    stock_not_found: int = 0
    items_with_additional: int = 0


class PedidoResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    status: str
    resumo: Optional[PedidoResumo] = None
    error_message: Optional[str] = None
    processing_time_seconds: Optional[float] = None

    class Config:
        from_attributes = True


class PedidoDetalheResponse(PedidoResponse):
    results: Optional[list[Any]] = None
    pedido_pdf_key: Optional[str] = None
    relatorio_pdf_key: Optional[str] = None
    template_excel_key: Optional[str] = None
    resultado_excel_key: Optional[str] = None


class PedidoListResponse(BaseModel):
    items: list[PedidoResponse]
    total: int
    page: int
    limit: int
    pages: int
