"""Generate Amazon Letter of Authorization — Fly International Trading Ltd → Faiz Mart."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "assets" / "Fly-International-Amazon-Authorization-Letter.pdf"

NAVY = (20, 20, 20)
ACCENT = (0, 90, 140)
MUTED = (80, 80, 80)

# Licensor — supplier / manufacturer
LICENSOR_NAME = "FLY INTERNATIONAL TRADING LTD"
LICENSOR_ADDRESS = (
    "Unit 1 Lawrence House, Derby Street, Manchester, UK, M8 8AT"
)
LICENSOR_CONTACT = "Will Yang"
LICENSOR_TITLE = "Director"
LICENSOR_EMAIL = "flyduvet@gmail.com"
LICENSOR_PHONE = "07411112207"

# Licensee — Amazon seller
LICENSEE_NAME = "FAIZ MART UK"
LICENSEE_ADDRESS = "41 Bransby Avenue, Manchester M9 6JN, United Kingdom"
LICENSEE_COMPANY_NO = "16882099"

ISSUE_DATE = date.today().strftime("%d %B %Y")
TERM_START = date.today().strftime("%d %B %Y")
TERM_END = "12 June 2028"

PRODUCTS = (
    "Mattress protectors; pillows; duvets and duvet sets; mattress toppers; "
    "bed sheets, pillowcases, and fitted sheets; bedding sets; and related "
    "home textile bedding products supplied or manufactured by Licensor."
)

AMAZON_MARKETPLACE = "Amazon.co.uk (United Kingdom)"


class AuthLetterPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("Helvetica", "I", 7.5)
        self.set_text_color(*MUTED)
        self.cell(
            0,
            6,
            f"{LICENSOR_NAME}  |  Authorization Ref: FIT-FMZ-001",
            align="C",
        )


def _section(doc: FPDF, title: str, body: str, margin: float) -> None:
    doc.set_font("Helvetica", "B", 10)
    doc.set_text_color(*NAVY)
    doc.multi_cell(0, 5.5, title)
    doc.ln(1)
    doc.set_font("Helvetica", "", 10)
    doc.set_text_color(30, 30, 30)
    doc.multi_cell(0, 5.5, body)
    doc.ln(4)


def generate() -> Path:
    doc = AuthLetterPDF(orientation="P", unit="mm", format="A4")
    doc.set_auto_page_break(auto=True, margin=22)
    doc.add_page()

    w = doc.w
    margin = 18

    # Letterhead — Licensor
    doc.set_xy(margin, 14)
    doc.set_font("Helvetica", "B", 11)
    doc.set_text_color(*NAVY)
    doc.multi_cell(w - 2 * margin, 5, LICENSOR_NAME)
    doc.set_font("Helvetica", "", 8.5)
    doc.set_text_color(*MUTED)
    doc.multi_cell(w - 2 * margin, 4.2, LICENSOR_ADDRESS)
    doc.ln(2)
    doc.cell(0, 4.5, f"Tel: {LICENSOR_PHONE}  |  Email: {LICENSOR_EMAIL}")

    doc.ln(4)
    doc.set_draw_color(180, 180, 180)
    doc.line(margin, doc.get_y(), w - margin, doc.get_y())
    doc.ln(6)

    doc.set_font("Helvetica", "", 10)
    doc.set_text_color(40, 40, 40)
    doc.cell(0, 5, f"Date: {ISSUE_DATE}")
    doc.ln(10)

    doc.set_font("Helvetica", "B", 13)
    doc.set_text_color(*NAVY)
    doc.cell(0, 8, "LETTER OF AUTHORIZATION", align="C", new_x="LMARGIN", new_y="NEXT")
    doc.ln(2)
    doc.set_font("Helvetica", "", 9.5)
    doc.set_text_color(*MUTED)
    doc.cell(0, 5, "For Amazon Seller Central - Product Listing & Sales Authorization", align="C")
    doc.ln(10)

    doc.set_font("Helvetica", "", 10)
    doc.set_text_color(30, 30, 30)
    doc.multi_cell(
        0,
        5.5,
        "To whom it may concern (including Amazon verification teams),\n\n"
        "Re: Letter of Authorization - Supply, Distribution & Amazon Marketplace Sales",
    )
    doc.ln(4)

    _section(
        doc,
        "1) LICENSOR",
        f"{LICENSOR_NAME} (\"Licensor\"), with its business address at {LICENSOR_ADDRESS}, "
        f"is the manufacturer, "
        f"wholesaler, and authorized supplier of the bedding and home textile products "
        f"described below.",
        margin,
    )

    _section(
        doc,
        "2) LICENSEE",
        f"{LICENSEE_NAME} (\"Licensee\"), company number {LICENSEE_COMPANY_NO}, "
        f"with registered address at {LICENSEE_ADDRESS}, is hereby authorized by "
        f"Licensor as set out in this letter.",
        margin,
    )

    _section(
        doc,
        "3) GRANT (Scope of Authorization)",
        f"Licensor hereby grants Licensee a non-exclusive authorization to purchase, "
        f"import, store, list, offer for sale, sell, and fulfil customer orders for "
        f"the following products on {AMAZON_MARKETPLACE}:\n\n"
        f"{PRODUCTS}\n\n"
        f"Scope of use on Amazon: product titles, bullet points, descriptions, "
        f"product images, packaging images, A+ content (where applicable), and "
        f"customer service relating to the authorized products supplied by Licensor.\n\n"
        f"Sublicensing: Not permitted without prior written consent from Licensor.\n\n"
        f"Consideration: Good and valuable consideration acknowledged, including "
        f"ongoing wholesale supply arrangements between the parties.",
        margin,
    )

    _section(
        doc,
        "4) GEOGRAPHIC SCOPE",
        f"Authorized territory: United Kingdom.\n"
        f"Authorized Amazon marketplace: {AMAZON_MARKETPLACE}.\n"
        f"Offline and other online channels: Only as separately agreed in writing.",
        margin,
    )

    _section(
        doc,
        "5) TERM",
        f"Effective from {TERM_START} until {TERM_END}, unless extended or terminated "
        f"earlier by either party on thirty (30) days' written notice.",
        margin,
    )

    doc.set_font("Helvetica", "B", 10)
    doc.set_text_color(*NAVY)
    doc.multi_cell(0, 5.5, "Amazon Verification / Contact")
    doc.ln(1)
    doc.set_font("Helvetica", "", 10)
    doc.set_text_color(30, 30, 30)
    doc.multi_cell(
        0,
        5.5,
        f"Licensor confirms this authorization is genuine and will respond to reasonable "
        f"verification inquiries from Amazon regarding this letter.\n\n"
        f"Contact: {LICENSOR_CONTACT}, {LICENSOR_TITLE}\n"
        f"Email: {LICENSOR_EMAIL}\n"
        f"Phone: {LICENSOR_PHONE}",
    )
    doc.ln(8)

    doc.set_font("Helvetica", "", 10)
    doc.cell(0, 6, "Yours faithfully,")
    doc.ln(12)
    doc.set_font("Helvetica", "I", 12)
    doc.set_text_color(*ACCENT)
    doc.cell(0, 8, LICENSOR_CONTACT)
    doc.ln(6)
    doc.set_font("Helvetica", "B", 10)
    doc.set_text_color(*NAVY)
    doc.cell(0, 6, LICENSOR_CONTACT.upper())
    doc.ln(5)
    doc.set_font("Helvetica", "", 10)
    doc.set_text_color(40, 40, 40)
    doc.cell(0, 5, LICENSOR_TITLE)
    doc.ln(4)
    doc.cell(0, 5, LICENSOR_NAME)
    doc.ln(4)
    doc.set_font("Helvetica", "", 9)
    doc.set_text_color(*MUTED)
    doc.cell(0, 5, f"Executed at Manchester, on {ISSUE_DATE}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.output(str(OUTPUT))
    return OUTPUT


if __name__ == "__main__":
    path = generate()
    print(f"Written: {path}")
