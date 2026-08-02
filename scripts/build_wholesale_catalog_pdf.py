"""Rebuild Rose-Empire-Wholesale-Catalog.pdf from catalog-data.json."""
import json
from datetime import date
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "catalog-data.json").read_text(encoding="utf-8"))
OUT = ROOT / "assets" / "Rose-Empire-Wholesale-Catalog.pdf"

navy = HexColor("#102241")
gold = HexColor("#b89549")
muted = HexColor("#5a6478")
sale = HexColor("#b42318")
line = HexColor("#e2dcd2")
bg = HexColor("#f6f4f0")
ink = HexColor("#0f1f35")


def main() -> None:
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "Brand",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=navy,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            "Sub",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=muted,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "HProd",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=navy,
            spaceBefore=10,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=ink,
            leading=12,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            "Meta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            textColor=muted,
            leading=11,
        )
    )
    styles.add(
        ParagraphStyle(
            "Foot",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=muted,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            "Sale",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=sale,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            "Cell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=ink,
        )
    )
    styles.add(
        ParagraphStyle(
            "CellSale",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=sale,
        )
    )
    styles.add(
        ParagraphStyle(
            "Was",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=muted,
        )
    )

    story = []
    story.append(Paragraph("ROSE EMPIRE", styles["Brand"]))
    story.append(Paragraph("WHOLESALE HOME TEXTILES", styles["Sub"]))
    story.append(
        Paragraph(
            "Mattress protectors &amp; bedding for hotels, care homes &amp; trade buyers",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            f"Wholesale Price Catalog · Updated {date.today().isoformat()}",
            styles["Meta"],
        )
    )
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=gold, spaceAfter=8))
    story.append(
        Paragraph(
            "Trade MOQ: 20 pieces per product size (1 trade box = 20 pieces; "
            "pillow-cover pairs may differ). Volume discounts: 10% off at 50+ pieces, "
            "20% off at 200+ pieces. Prices ex VAT. UK shipping: Mainland £10 / "
            "Scotland &amp; NI £15 per trade box. Formal quotes via website RFQ or email.",
            styles["Meta"],
        )
    )
    story.append(Spacer(1, 8))

    for product in DATA.get("products", []):
        block = []
        tag = product.get("tag") or (product.get("promo") or {}).get("label") or ""
        title = product.get("title", "")
        heading = f"{title} &nbsp;[{tag}]" if tag else title
        block.append(Paragraph(heading, styles["HProd"]))

        promo = product.get("promo")
        if promo:
            detail = promo.get("detail") or f"Save £{float(promo.get('amountOff') or 0.5):.2f} on every size"
            block.append(Paragraph(f"TRADE SALE — {detail}", styles["Sale"]))

        block.append(Paragraph(product.get("desc", ""), styles["Body"]))

        rows = [
            [
                Paragraph("<b>Size</b>", styles["Cell"]),
                Paragraph("<b>Was</b>", styles["Cell"]),
                Paragraph("<b>Trade unit price (ex VAT)</b>", styles["Cell"]),
            ]
        ]
        prices = []
        for size in product.get("sizes", []):
            price = float(size.get("price") or 0)
            was = float(size.get("wasPrice") or 0)
            prices.append(price)
            name = size.get("name", "")
            if was > price:
                rows.append(
                    [
                        Paragraph(name, styles["Cell"]),
                        Paragraph(f"£{was:.2f}", styles["Was"]),
                        Paragraph(f"<b>£{price:.2f}</b>", styles["CellSale"]),
                    ]
                )
            else:
                rows.append(
                    [
                        Paragraph(name, styles["Cell"]),
                        Paragraph("—", styles["Was"]),
                        Paragraph(f"£{price:.2f}", styles["Cell"]),
                    ]
                )

        table = Table(rows, colWidths=[95 * mm, 25 * mm, 55 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), bg),
                    ("TEXTCOLOR", (0, 0), (-1, 0), navy),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.4, line),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        block.append(table)

        if prices:
            low = min(prices)
            block.append(Spacer(1, 4))
            block.append(
                Paragraph(
                    f"From <b>£{low:.2f}</b> per unit (MOQ {product.get('moq', 20)})",
                    styles["Meta"],
                )
            )

        highs = product.get("highlights") or []
        if highs:
            block.append(Paragraph(" &nbsp;|&nbsp; ".join(highs), styles["Meta"]))

        block.append(Spacer(1, 6))
        block.append(HRFlowable(width="100%", thickness=0.5, color=line, spaceAfter=4))
        story.append(KeepTogether(block))

    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "www.roseempire.co.uk &nbsp;|&nbsp; info@roseempire.co.uk &nbsp;|&nbsp; +44 7999 988450<br/>"
            "Manchester manufacturer-direct · Quotes answered within 1 business day",
            styles["Foot"],
        )
    )

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="Rose Empire Wholesale Catalog",
        author="Rose Empire Wholesale Home Textiles",
    )
    doc.build(story)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")

    text = "\n".join((p.extract_text() or "") for p in PdfReader(str(OUT)).pages)
    for needle in ("TRADE SALE", "4.70", "5.20", "3.90", "Terry"):
        assert needle in text, f"missing {needle}"
    print("verified Terry sale prices present in PDF")


if __name__ == "__main__":
    main()
