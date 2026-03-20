import shutil
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from api.routes import health as health_router
from api.routes import pedidos as pedidos_router
from calculator import compute_adjustments, load_template_rows
from core.logging import setup_logging
from excel_exporter import export_adjustment_excel
from parser_pedido import parse_order_pdf
from parser_relatorio import parse_sales_report_pdf

setup_logging()

app = FastAPI(title="PedidoBK API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restringir quando adicionar autenticação
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers v1
app.include_router(health_router.router)
app.include_router(pedidos_router.router)

# ──────────────────────────────────────────────
# Endpoints legados (mantidos para compatibilidade com v0)
# ──────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {"message": "PedidoBK API v1 online"}


@app.post("/process")
async def process_files(
    pedido_pdf: UploadFile = File(...),
    relatorio_pdf: UploadFile = File(...),
    template_xlsx: UploadFile = File(...),
):
    request_id = uuid.uuid4().hex[:10]
    work_dir = UPLOAD_DIR / request_id
    work_dir.mkdir(parents=True, exist_ok=True)

    pedido_path = work_dir / (pedido_pdf.filename or "pedido.pdf")
    relatorio_path = work_dir / (relatorio_pdf.filename or "relatorio.pdf")
    template_path = work_dir / (template_xlsx.filename or "template.xlsx")
    output_name = f"pedido-{datetime.now().date()}.xlsx"
    output_path = OUTPUT_DIR / f"{request_id}-{output_name}"

    try:
        with open(pedido_path, "wb") as f:
            shutil.copyfileobj(pedido_pdf.file, f)
        with open(relatorio_path, "wb") as f:
            shutil.copyfileobj(relatorio_pdf.file, f)
        with open(template_path, "wb") as f:
            shutil.copyfileobj(template_xlsx.file, f)

        order_items = parse_order_pdf(str(pedido_path))
        stock_data = parse_sales_report_pdf(str(relatorio_path))
        _, _, template_rows = load_template_rows(str(template_path))
        results = compute_adjustments(order_items, stock_data, template_rows)
        export_adjustment_excel(str(template_path), str(output_path), results)

        summary = {
            "order_items_found": len(order_items),
            "processed_ok": sum(1 for r in results if r["status"] == "ok"),
            "template_not_found": sum(1 for r in results if r["status"] == "template_not_found"),
            "stock_not_found": sum(1 for r in results if r["status"] == "stock_not_found"),
            "items_with_additional": sum(1 for r in results if r["status"] == "ok" and r["additional_packs"] > 0),
        }

        response = FileResponse(
            path=str(output_path),
            filename=output_name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response.headers["X-PedidoBK-Summary"] = str(summary)
        return response
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


@app.post("/preview")
async def preview_files(
    pedido_pdf: UploadFile = File(...),
    relatorio_pdf: UploadFile = File(...),
    template_xlsx: UploadFile = File(...),
):
    request_id = uuid.uuid4().hex[:10]
    work_dir = UPLOAD_DIR / request_id
    work_dir.mkdir(parents=True, exist_ok=True)

    pedido_path = work_dir / (pedido_pdf.filename or "pedido.pdf")
    relatorio_path = work_dir / (relatorio_pdf.filename or "relatorio.pdf")
    template_path = work_dir / (template_xlsx.filename or "template.xlsx")

    try:
        with open(pedido_path, "wb") as f:
            shutil.copyfileobj(pedido_pdf.file, f)
        with open(relatorio_path, "wb") as f:
            shutil.copyfileobj(relatorio_pdf.file, f)
        with open(template_path, "wb") as f:
            shutil.copyfileobj(template_xlsx.file, f)

        order_items = parse_order_pdf(str(pedido_path))
        stock_data = parse_sales_report_pdf(str(relatorio_path))
        _, _, template_rows = load_template_rows(str(template_path))
        results = compute_adjustments(order_items, stock_data, template_rows)

        return JSONResponse({
            "report_date": str(stock_data.get("report_date")),
            "summary": {
                "order_items_found": len(order_items),
                "processed_ok": sum(1 for r in results if r["status"] == "ok"),
                "template_not_found": sum(1 for r in results if r["status"] == "template_not_found"),
                "stock_not_found": sum(1 for r in results if r["status"] == "stock_not_found"),
                "items_with_additional": sum(1 for r in results if r["status"] == "ok" and r["additional_packs"] > 0),
            },
            "results": results,
        })
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
