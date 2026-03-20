import re
from datetime import datetime
import pdfplumber


def _normalize_code(value) -> str:
    text = str(value).strip()
    return text.lstrip("0") or "0"


def parse_sales_report_pdf(pdf_path: str) -> dict:
    report_date = None
    items = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=1, y_tolerance=1, layout=True) or ""

            if report_date is None:
                match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", text)
                if match:
                    report_date = datetime.strptime(match.group(1), "%d/%m/%Y").date()

            words = page.extract_words(
                x_tolerance=1,
                y_tolerance=1,
                keep_blank_chars=False,
            )

            groups = {}
            for word in words:
                top = round(word["top"], 1)
                groups.setdefault(top, []).append(word)

            for _, line_words in sorted(groups.items()):
                line = sorted(line_words, key=lambda w: w["x0"])
                if not line:
                    continue

                first = line[0]["text"]

                if not re.fullmatch(r"\d{3,8}", first):
                    continue

                if line[0]["x0"] > 60:
                    continue

                description_tokens = []
                item = {
                    "code": _normalize_code(first),
                    "description": "",
                    "disp": 0,
                    "mes": 0,
                    "m1": 0,
                    "m2": 0,
                    "m3": 0,
                }

                for word in line[1:]:
                    x = word["x0"]
                    text = word["text"]

                    if x < 250:
                        description_tokens.append(text)
                    elif x < 280 and re.fullmatch(r"-?\d+", text):
                        item["disp"] = int(text)
                    elif 410 <= x < 432 and re.fullmatch(r"-?\d+", text):
                        item["mes"] = int(text)
                    elif 432 <= x < 454 and re.fullmatch(r"-?\d+", text):
                        item["m1"] = int(text)
                    elif 454 <= x < 476 and re.fullmatch(r"-?\d+", text):
                        item["m2"] = int(text)
                    elif 476 <= x < 502 and re.fullmatch(r"-?\d+", text):
                        item["m3"] = int(text)

                item["description"] = " ".join(description_tokens).strip()
                items.append(item)

    return {
        "report_date": report_date,
        "items": items,
    }
