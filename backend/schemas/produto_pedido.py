from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ProdutoPedidoResponse(BaseModel):
    id: UUID
    pedido_id: UUID

    # Dados do template (planilha de produtos da fábrica)
    codigo: str
    descricao: str
    tamanho_embalagem: int
    linha_template: Optional[int] = None

    # Quantidades
    qp: int          # quantidade pedida (do PDF do pedido)
    qa: int          # quantidade adicional (calculada)
    total: int       # qp + qa

    # Recebimento via XML NF-e
    qtd_recebida: Optional[int] = None

    # Status do item no processamento
    status: str      # ok | template_not_found | stock_not_found

    created_at: datetime

    class Config:
        from_attributes = True


class ProdutoPedidoListResponse(BaseModel):
    pedido_id: UUID
    items: list[ProdutoPedidoResponse]
    total: int
