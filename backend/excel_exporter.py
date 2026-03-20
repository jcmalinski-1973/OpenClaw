import openpyxl


def export_adjustment_excel(template_path: str, output_path: str, results: list[dict]) -> None:
    workbook = openpyxl.load_workbook(template_path)
    sheet = workbook[workbook.sheetnames[0]]

    for row_idx in range(4, sheet.max_row + 1):
        sheet.cell(row_idx, 4).value = None

    for item in results:
        if item.get("status") != "ok":
            continue
        sheet.cell(item["template_row"], 4).value = item["additional_packs"]

    workbook.save(output_path)


def export_from_produtos(template_path: str, output_path: str, produtos) -> None:
    """Gera o Excel de saída a partir dos registros de ProdutoPedido do banco."""
    workbook = openpyxl.load_workbook(template_path)
    sheet = workbook[workbook.sheetnames[0]]

    for row_idx in range(4, sheet.max_row + 1):
        sheet.cell(row_idx, 4).value = None

    for p in produtos:
        if p.status != "ok" or not p.linha_template:
            continue
        sheet.cell(p.linha_template, 4).value = p.qa

    workbook.save(output_path)
