import os
import re
import io
from datetime import datetime

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF

from config import LOGO_PATH


def format_docx(text: str, doc_type: str) -> bytes:
    document = Document()
    style = document.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    if os.path.exists(LOGO_PATH):
        try:
            p = document.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(LOGO_PATH, width=Inches(1.2))
        except Exception:
            pass

    title = document.add_heading(doc_type or "Legal Document", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            document.add_paragraph("")
            continue
        if re.match(r"^(\d+\.|Section\s+\d+|ARTICLE\s+\w+)", stripped, re.IGNORECASE):
            document.add_heading(stripped, level=2)
        else:
            document.add_paragraph(stripped)

    section = document.sections[0]
    footer_para = section.footer.paragraphs[0]
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_para.text = (
        f"LegalEase Inc. | contact@legalease.com | "
        f"Generated on {datetime.now().strftime('%Y-%m-%d')}"
    )

    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


class _LegalPDF(FPDF):
    def __init__(self, doc_type: str):
        super().__init__()
        self.doc_type = doc_type
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if os.path.exists(LOGO_PATH):
            try:
                self.image(LOGO_PATH, x=85, y=8, w=40)
                self.ln(28)
            except Exception:
                pass
        self.set_font("Times", "B", 16)
        self.cell(0, 10, self.doc_type or "Legal Document", align="C", ln=True)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Times", "I", 8)
        self.cell(
            0, 10,
            f"LegalEase Inc. | contact@legalease.com | Page {self.page_no()}",
            align="C",
        )


def _clean_latin(text: str) -> str:
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",
        "\u2026": "...", "\u00a0": " ",
        "\u2022": "-",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "replace").decode("latin-1")


def format_pdf(text: str, doc_type: str) -> bytes:
    pdf = _LegalPDF(doc_type)
    pdf.add_page()
    pdf.set_font("Times", size=11)

    for line in text.split("\n"):
        stripped = _clean_latin(line.strip())
        if not stripped:
            pdf.ln(4)
            continue
        if re.match(r"^(\d+\.|Section\s+\d+|ARTICLE\s+\w+)", stripped, re.IGNORECASE):
            pdf.set_font("Times", "B", 12)
            pdf.multi_cell(0, 7, stripped)
            pdf.set_font("Times", size=11)
        else:
            pdf.multi_cell(0, 6, stripped)

    out = pdf.output(dest="S")
    if isinstance(out, str):
        out = out.encode("latin-1", "replace")
    return bytes(out)


def format_html_preview(text: str) -> str:
    if not text:
        return ""
    html_lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            html_lines.append("<br/>")
            continue
        safe = stripped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if re.match(r"^(\d+\.|Section\s+\d+|ARTICLE\s+\w+)", stripped, re.IGNORECASE):
            html_lines.append(
                f"<h4 style='color:#7dd3fc; margin-top:16px; margin-bottom:6px;'>{safe}</h4>"
            )
        else:
            html_lines.append(
                f"<p style='color:#e2e8f0; margin:4px 0; line-height:1.5;'>{safe}</p>"
            )
    return "".join(html_lines)