"""Generate Rose Empire wholesale product & price PDF from catalog-data.json."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent
CATALOG_JSON = ROOT / "catalog-data.json"
OUTPUT_FILES = (
    ROOT / "assets" / "Rose-Empire-Wholesale-Catalog.pdf",
    ROOT / "Rose-Empire-Wholesale-Catalog.pdf",
)

NAVY = (13, 31, 60)
GOLD = (201, 164, 68)
MUTED = (90, 106, 133)
LINE = (216, 221, 232)


class CatalogPDF(FPDF):
    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 8, "Rose Empire Wholesale Catalog", align="L")
        self.cell(0, 8, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 8, "www.roseempire.co.uk  |  info@roseempire.co.uk  |  +44 7999 988450", align="C")


def _category_label(category: str) -> str:
    if category == "protectors":
        return "Mattress Protectors"
    if category == "pillows":
        return "Pillows"
    return "Wholesale Textiles"


def _ascii(text: str) -> str:
    """Helvetica-safe text for fpdf2 core fonts."""
    if not text:
        return ""
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u00d7": "x",
        "\u00a3": "GBP ",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _money(value: float) -> str:
    return f"GBP {value:.2f}"


def generate_pdf(catalog_path: Path = CATALOG_JSON) -> Path:
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    contact = data.get("contact", {})
    wholesale = data.get("wholesale", {})
    products = data.get("products", [])

    doc = CatalogPDF(orientation="P", unit="mm", format="A4")
    doc.set_auto_page_break(auto=True, margin=18)
    doc.add_page()

    w = doc.w
    doc.set_fill_color(*NAVY)
    doc.rect(0, 0, w, 48, style="F")
    doc.set_fill_color(*GOLD)
    doc.rect(0, 48, w, 2.5, style="F")

    doc.set_xy(14, 14)
    doc.set_font("Helvetica", "B", 24)
    doc.set_text_color(255, 255, 255)
    doc.cell(0, 10, "ROSE EMPIRE")
    doc.set_font("Helvetica", "", 9)
    doc.set_text_color(*GOLD)
    doc.set_xy(14, 24)
    doc.cell(0, 5, "WHOLESALE HOME TEXTILES")
    doc.set_text_color(220, 228, 240)
    doc.set_xy(14, 32)
    doc.cell(0, 5, "Mattress protectors & bedding for hotels, care homes & trade buyers")

    doc.set_xy(14, 56)
    doc.set_font("Helvetica", "B", 16)
    doc.set_text_color(*NAVY)
    doc.cell(0, 8, "Wholesale Price Catalog")
    doc.set_font("Helvetica", "", 9)
    doc.set_text_color(*MUTED)
    updated = data.get("updatedAt", date.today().isoformat())
    doc.cell(0, 8, f"Updated {updated}", align="R", new_x="LMARGIN", new_y="NEXT")

    doc.ln(2)
    moq = wholesale.get("moqPerSize", 20)
    box = wholesale.get("boxLabel", "1 trade box = 20 pieces")
    doc.set_font("Helvetica", "", 10)
    doc.set_text_color(40, 40, 40)
    doc.multi_cell(
        0,
        5,
        f"Trade MOQ: {moq} pieces per product size ({box}). "
        "Volume discounts: 10% off at 50+ pieces, 20% off at 200+ pieces. "
        "Prices ex VAT. Formal quotes via website RFQ or email.",
    )
    doc.ln(4)

    for product in products:
        if doc.get_y() > 240:
            doc.add_page()

        y0 = doc.get_y()
        doc.set_fill_color(*NAVY)
        doc.rect(14, y0, w - 28, 10, style="F")
        doc.set_xy(16, y0 + 2.5)
        doc.set_font("Helvetica", "B", 11)
        doc.set_text_color(255, 255, 255)
        title = _ascii(product.get("title", "Product"))
        tag = product.get("tag") or ""
        if tag:
            title = f"{title}  [{_ascii(tag)}]"
        doc.cell(0, 6, title)
        doc.ln(12)

        doc.set_font("Helvetica", "", 9)
        doc.set_text_color(50, 50, 50)
        desc = _ascii((product.get("desc") or "")[:280])
        doc.multi_cell(0, 4.5, desc)
        doc.ln(2)

        doc.set_font("Helvetica", "B", 9)
        doc.set_text_color(*NAVY)
        doc.cell(0, 5, _category_label(product.get("category", "")), new_x="LMARGIN", new_y="NEXT")
        doc.ln(1)

        # Price table header
        doc.set_fill_color(*LINE)
        doc.set_font("Helvetica", "B", 8)
        doc.set_text_color(*NAVY)
        col_w = (w - 28) / 2
        doc.cell(col_w, 7, "Size", border=1, fill=True)
        doc.cell(col_w, 7, "Trade unit price (ex VAT)", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        doc.set_font("Helvetica", "", 8)
        doc.set_text_color(40, 40, 40)
        for size in product.get("sizes", []):
            doc.cell(col_w, 6, _ascii(size.get("name", "")), border=1)
            doc.cell(col_w, 6, _money(float(size.get("price", 0))), border=1, new_x="LMARGIN", new_y="NEXT")

        base = product.get("basePrice")
        if base is not None:
            doc.set_font("Helvetica", "I", 8)
            doc.set_text_color(*MUTED)
            doc.cell(0, 5, f"From {_money(float(base))} per unit (MOQ {product.get('moq', moq)})", new_x="LMARGIN", new_y="NEXT")

        highlights = product.get("highlights") or []
        if highlights:
            doc.set_font("Helvetica", "", 8)
            doc.set_text_color(*GOLD)
            doc.cell(0, 5, "  |  ".join(_ascii(h) for h in highlights[:5]), new_x="LMARGIN", new_y="NEXT")

        doc.ln(6)

    doc.add_page()
    doc.set_font("Helvetica", "B", 14)
    doc.set_text_color(*NAVY)
    doc.cell(0, 10, "How to order")
    doc.ln(4)
    doc.set_font("Helvetica", "", 10)
    doc.set_text_color(40, 40, 40)
    site = contact.get("siteUrl", "https://www.roseempire.co.uk")
    steps = (
        f"1. Browse the live catalog at {site}",
        "2. Add products to the quote cart and submit the RFQ form",
        "3. Receive a formal PDF quote within 24 hours",
        f"4. Email {contact.get('email', 'info@roseempire.co.uk')} or call {contact.get('phoneDisplay', '+44 7999 988450')}",
    )
    for step in steps:
        doc.multi_cell(0, 6, step)
        doc.ln(1)

    doc.ln(6)
    doc.set_fill_color(*GOLD)
    doc.rect(14, doc.get_y(), w - 28, 1, style="F")
    doc.ln(4)
    doc.set_font("Helvetica", "B", 10)
    doc.set_text_color(*NAVY)
    doc.cell(0, 6, "Rose Empire Wholesale  |  UK-wide delivery for trade buyers")

    primary = OUTPUT_FILES[0]
    primary.parent.mkdir(parents=True, exist_ok=True)
    doc.output(str(primary))
    for alt in OUTPUT_FILES[1:]:
        alt.write_bytes(primary.read_bytes())
    return primary


def _cli() -> int:
    path = generate_pdf()
    print(f"Catalog PDF written: {path}")
    print(f"Also copied to: {OUTPUT_FILES[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
