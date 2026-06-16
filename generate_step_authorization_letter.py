"""Generate readable STEP Brand Authorization Letter (Amazon)."""
from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "assets" / "STEP-Brand-Authorization-Letter.pdf"

NAVY = (20, 20, 20)
GREEN = (34, 120, 60)
MUTED = (80, 80, 80)

SUPPLIER_NAME = "SAISYNC CONSULTANTS PRIVATE LIMITED"
SUPPLIER_ADDRESS = "Unit 1, Lawrence House, Derby Street, Manchester M8 8AT, United Kingdom"
SUPPLIER_PHONE = "080-61568261 / 7090911986"

PRODUCTS = (
    "Electric Vehicles; Automobiles; Motors for Motorcycles, Motors for Bicycles, "
    "Motors for Cycles, Motors for Automobiles, Electric Motors for Motor Cars; "
    "Vehicle Parts, Automobile Spares, Automotive Components, Electric Land Vehicles "
    "(including Battery/Electrically Operated Vehicles), Parts, Bicycles, Tricycles, "
    "Parts, Fittings and Accessories - Cable Ties"
)


class AuthLetterPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 8, f"Authorization No. 001  |  TM Application 6095020  |  Class 12", align="C")


def generate() -> Path:
    doc = AuthLetterPDF(orientation="P", unit="mm", format="A4")
    doc.set_auto_page_break(auto=True, margin=20)
    doc.add_page()

    w = doc.w
    margin = 18

    # Header — brand
    doc.set_xy(margin, 16)
    doc.set_font("Helvetica", "B", 22)
    doc.set_text_color(*NAVY)
    doc.cell(80, 10, "STEP")
    doc.set_font("Helvetica", "B", 10)
    doc.set_text_color(*GREEN)
    doc.set_xy(margin, 26)
    doc.cell(80, 6, "GO ELECTRIC")

    # Header — supplier (top right)
    doc.set_font("Helvetica", "B", 9)
    doc.set_text_color(*NAVY)
    doc.set_xy(110, 16)
    doc.multi_cell(82, 4.5, SUPPLIER_NAME, align="R")
    doc.set_font("Helvetica", "", 8.5)
    doc.set_text_color(*MUTED)
    doc.set_x(110)
    doc.multi_cell(82, 4.2, SUPPLIER_ADDRESS, align="R")
    doc.set_x(110)
    doc.cell(82, 5, SUPPLIER_PHONE, align="R")

    doc.ln(8)
    doc.set_draw_color(200, 200, 200)
    doc.line(margin, 42, w - margin, 42)

    # Recipient block
    y = 50
    doc.set_xy(margin, y)
    doc.set_font("Helvetica", "B", 10)
    doc.set_text_color(*NAVY)
    doc.cell(0, 6, "JAGADISH PATIL")
    doc.ln(5)
    doc.set_font("Helvetica", "", 10)
    doc.set_text_color(40, 40, 40)
    doc.cell(0, 5, "Director")
    doc.ln(5)
    doc.cell(0, 5, "Saisync Consultants Private Limited")
    doc.ln(12)

    # Title
    doc.set_font("Helvetica", "B", 14)
    doc.set_text_color(*NAVY)
    doc.cell(0, 10, "BRAND AUTHORIZATION LETTER", align="C", new_x="LMARGIN", new_y="NEXT")
    doc.ln(6)

    # Body
    doc.set_font("Helvetica", "", 10.5)
    doc.set_text_color(30, 30, 30)
    body1 = (
        f"This is to certify that {SUPPLIER_NAME}, located at {SUPPLIER_ADDRESS}, "
        f"is authorised to supply, promote, distribute, sell, exhibit, negotiate and hold "
        f"responsibility for after-sale services of the STEP trademark in India."
    )
    doc.multi_cell(0, 6, body1)
    doc.ln(4)

    doc.set_font("Helvetica", "B", 10.5)
    doc.multi_cell(0, 6, "The STEP trademark includes the following products:")
    doc.ln(2)

    doc.set_font("Helvetica", "", 10)
    doc.multi_cell(0, 5.5, PRODUCTS)
    doc.ln(6)

    # Legal details box
    doc.set_fill_color(248, 248, 248)
    doc.set_font("Helvetica", "", 10)
    y0 = doc.get_y()
    doc.rect(margin, y0, w - 2 * margin, 28, style="F")
    doc.set_xy(margin + 4, y0 + 4)
    details = (
        "TM Application Number: 6095020\n"
        "TM Class: 12\n"
        "Validity: 29 December 2023 to 29 December 2028\n"
        "Authorization Number: 001"
    )
    doc.multi_cell(w - 2 * margin - 8, 5.5, details)
    doc.ln(14)

    # Signature
    doc.set_font("Helvetica", "", 10)
    doc.cell(0, 6, "Yours sincerely,")
    doc.ln(14)
    doc.set_font("Helvetica", "I", 11)
    doc.set_text_color(0, 60, 140)
    doc.cell(0, 8, "Jagadish Patil")
    doc.ln(6)
    doc.set_font("Helvetica", "B", 10)
    doc.set_text_color(*NAVY)
    doc.cell(0, 6, "JAGADISH PATIL")
    doc.ln(5)
    doc.set_font("Helvetica", "", 10)
    doc.set_text_color(40, 40, 40)
    doc.cell(0, 6, "Brand Owner")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.output(str(OUTPUT))
    return OUTPUT


if __name__ == "__main__":
    path = generate()
    print(f"Written: {path}")
