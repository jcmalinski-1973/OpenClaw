import re
import pdfplumber


def _normalize_code(value) -> str:
    text = str(value).strip()
    return text.lstrip("0") or "0"


def parse_order_pdf(pdf_path: str) -> list[dict]:
    items = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
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

                if not any(word["x0"] > 430 for word in line):
                    continue

                description_tokens = []
                pack_type = None
                suggested_packs = None

                for word in line[1:]:
                    x = word["x0"]
                    text = word["text"]

                    if x < 325:
                        description_tokens.append(text)
                    elif 438 <= x < 451 and text in {"CX", "FD", "PCT"}:
                        pack_type = text
                    elif 451 <= x < 470 and re.fullmatch(r"\d+", text):
                        suggested_packs = int(text)

                if not pack_type or suggested_packs is None:
                    continue

                items.append(
                    {
                        "code": _normalize_code(first),
                        "description": " ".join(description_tokens).strip(),
                        "suggested_packs": suggested_packs,
                        "pack_type": pack_type,
                    }
                )

    return items
