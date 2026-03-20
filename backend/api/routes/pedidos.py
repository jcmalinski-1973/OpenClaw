import logging
import math
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.session import get_db
from models.pedido import Pedido
from schemas.pedido import PedidoDetalheResponse, PedidoListResponse, PedidoResponse
from services.pedido_service import create_pedido
from storage import get_storage

router = APIRouter(prefix="/pedidos", tags=["pedidos"])
logger = logging.getLogger(__name__)


@router.post("", response_model=PedidoResponse, status_code=201)
async def criar_pedido(
    pedido_pdf: UploadFile = File(...),
    relatorio_pdf: UploadFile = File(...),
    template_xlsx: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    pedido = create_pedido(
        db=db,
        storage=get_storage(),
        pedido_pdf_bytes=await pedido_pdf.read(),
        relatorio_pdf_bytes=await relatorio_pdf.read(),
        template_excel_bytes=await template_xlsx.read(),
        pedido_pdf_name=pedido_pdf.filename or "pedido.pdf",
        relatorio_pdf_name=relatorio_pdf.filename or "relatorio.pdf",
        template_excel_name=template_xlsx.filename or "template.xlsx",
    )
    return pedido


@router.get("", response_model=PedidoListResponse)
def listar_pedidos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Pedido)

    if status:
        query = query.filter(Pedido.status == status)

    total = query.count()
    pages = math.ceil(total / limit) if total > 0 else 1
    items = (
        query.order_by(Pedido.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return PedidoListResponse(items=items, total=total, page=page, limit=limit, pages=pages)


@router.get("/{pedido_id}", response_model=PedidoDetalheResponse)
def obter_pedido(pedido_id: UUID, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido


@router.get("/{pedido_id}/resultado")
def baixar_resultado(pedido_id: UUID, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.status != "completed" or not pedido.resultado_excel_key:
        raise HTTPException(status_code=404, detail="Resultado não disponível")

    content = get_storage().read_bytes(pedido.resultado_excel_key)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=pedido-{pedido_id}.xlsx"},
    )


@router.get("/{pedido_id}/arquivos")
def listar_arquivos(pedido_id: UUID, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    return {
        "pedido_id": str(pedido_id),
        "arquivos": {
            "pedido_pdf": pedido.pedido_pdf_key,
            "relatorio_pdf": pedido.relatorio_pdf_key,
            "template_excel": pedido.template_excel_key,
            "resultado_excel": pedido.resultado_excel_key,
        },
    }
