import logging
import shutil
import tempfile
import time
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from calculator import compute_adjustments, load_template_rows
from core.config import settings
from excel_exporter import export_adjustment_excel
from models.pedido import Pedido
from models.produto_pedido import ProdutoPedido
from parser_pedido import parse_order_pdf
from parser_relatorio import parse_sales_report_pdf
from storage.base import StorageBackend

logger = logging.getLogger(__name__)


def _gcs_key(pedido_id: UUID, filename: str) -> str:
    return f"{settings.GCS_PREFIX}/{pedido_id}/{filename}"


def create_pedido(
    db: Session,
    storage: StorageBackend,
    pedido_pdf_bytes: bytes,
    relatorio_pdf_bytes: bytes,
    template_excel_bytes: bytes,
    pedido_pdf_name: str,
    relatorio_pdf_name: str,
    template_excel_name: str,
) -> Pedido:
    pedido = Pedido(status="processing")
    db.add(pedido)
    db.commit()
    db.refresh(pedido)

    logger.info("Pedido criado: %s", pedido.id)

    start = time.time()
    work_dir = Path(tempfile.mkdtemp())

    try:
        # Salvar arquivos localmente para processamento
        pedido_path = work_dir / pedido_pdf_name
        relatorio_path = work_dir / relatorio_pdf_name
        template_path = work_dir / template_excel_name
        output_path = work_dir / "resultado.xlsx"

        pedido_path.write_bytes(pedido_pdf_bytes)
        relatorio_path.write_bytes(relatorio_pdf_bytes)
        template_path.write_bytes(template_excel_bytes)

        # Upload dos arquivos de entrada para GCS
        pedido_key = _gcs_key(pedido.id, "pedido.pdf")
        relatorio_key = _gcs_key(pedido.id, "relatorio.pdf")
        template_key = _gcs_key(pedido.id, "template.xlsx")

        storage.upload(str(pedido_path), pedido_key)
        storage.upload(str(relatorio_path), relatorio_key)
        storage.upload(str(template_path), template_key)

        pedido.pedido_pdf_key = pedido_key
        pedido.relatorio_pdf_key = relatorio_key
        pedido.template_excel_key = template_key
        db.commit()

        # Processamento (núcleo existente — sem alteração)
        order_items = parse_order_pdf(str(pedido_path))
        stock_data = parse_sales_report_pdf(str(relatorio_path))
        _, _, template_rows = load_template_rows(str(template_path))
        results = compute_adjustments(order_items, stock_data, template_rows)

        export_adjustment_excel(
            template_path=str(template_path),
            output_path=str(output_path),
            results=results,
        )

        # Upload resultado para GCS
        resultado_key = _gcs_key(pedido.id, "resultado.xlsx")
        storage.upload(str(output_path), resultado_key)

        resumo = {
            "order_items_found": len(order_items),
            "processed_ok": sum(1 for r in results if r["status"] == "ok"),
            "template_not_found": sum(1 for r in results if r["status"] == "template_not_found"),
            "stock_not_found": sum(1 for r in results if r["status"] == "stock_not_found"),
            "items_with_additional": sum(
                1 for r in results if r["status"] == "ok" and r["additional_packs"] > 0
            ),
        }

        # Persistir itens do pedido na tabela produtos_pedido
        for r in results:
            qp = r.get("suggested_packs", 0) or 0
            qa = r.get("additional_packs", 0) or 0
            db.add(ProdutoPedido(
                pedido_id=pedido.id,
                codigo=r.get("template_code") or r.get("code", ""),
                descricao=r.get("template_description") or r.get("description", ""),
                tamanho_embalagem=r.get("pack_size", 0) or 0,
                linha_template=r.get("template_row"),
                qp=qp,
                qa=qa,
                total=qp + qa,
                status=r.get("status", "ok"),
            ))

        pedido.status = "completed"
        pedido.resultado_excel_key = resultado_key
        pedido.resumo = resumo
        pedido.results = results
        pedido.processing_time_seconds = round(time.time() - start, 2)
        db.commit()
        db.refresh(pedido)

        logger.info("Pedido concluído: %s em %.2fs", pedido.id, pedido.processing_time_seconds)
        return pedido

    except Exception as exc:
        logger.exception("Erro ao processar pedido %s: %s", pedido.id, exc)
        pedido.status = "failed"
        pedido.error_message = str(exc)
        pedido.processing_time_seconds = round(time.time() - start, 2)
        db.commit()
        db.refresh(pedido)
        return pedido

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
