import os
import json
import csv
import io
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

logger = logging.getLogger(__name__)

EXPORTS_DIR = os.path.join(os.getcwd(), "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)


class NumberedCanvas(canvas.Canvas):
    """Adds 'Page X of Y' and header to all pages of ReportLab PDF."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header
        self.drawString(54, 750, "STEAM INTELLIGENCE — INFORME DE MERCADO")
        self.setStrokeColor(colors.HexColor("#334155"))
        self.setLineWidth(0.5)
        self.line(54, 744, 558, 744)

        # Footer
        self.line(54, 45, 558, 45)
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 34, page_text)
        self.drawString(54, 34, "Confidencial & Privado · No constituye promesa de ventas ni asesoramiento financiero.")
        self.restoreState()


class ExportService:
    @staticmethod
    def generate_json_export(report_data: Dict[str, Any], filename: str) -> str:
        """Generates reproducible structured JSON export."""
        filepath = os.path.join(EXPORTS_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        return filepath

    @staticmethod
    def generate_csv_export(rows: List[Dict[str, Any]], filename: str) -> str:
        """Generates flat CSV export."""
        filepath = os.path.join(EXPORTS_DIR, filename)
        if not rows:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("no_data\n")
            return filepath

        fieldnames = list(rows[0].keys())
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return filepath

    @staticmethod
    def generate_xlsx_export(sheets_data: Dict[str, List[Dict[str, Any]]], filename: str) -> str:
        """Generates multi-sheet formatted Excel workbook."""
        filepath = os.path.join(EXPORTS_DIR, filename)
        wb = openpyxl.Workbook()
        # Remove default sheet
        wb.remove(wb.active)

        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        for sheet_name, rows in sheets_data.items():
            ws = wb.create_sheet(title=sheet_name[:31])
            if not rows:
                ws.append(["Sin datos disponibles"])
                continue

            fieldnames = list(rows[0].keys())
            ws.append(fieldnames)

            for col_idx in range(1, len(fieldnames) + 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center")

            for r_idx, row in enumerate(rows, start=2):
                ws.append([str(row.get(k, "")) for k in fieldnames])
                for col_idx in range(1, len(fieldnames) + 1):
                    ws.cell(row=r_idx, column=col_idx).border = border

            # Auto-adjust column width
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = openpyxl.utils.get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        wb.save(filepath)
        return filepath

    @staticmethod
    def generate_pdf_export(report_data: Dict[str, Any], filename: str) -> str:
        """Generates professional printable PDF report with selectable text."""
        filepath = os.path.join(EXPORTS_DIR, filename)
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=60,
            bottomMargin=50
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a")
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#475569")
        )
        h2_style = ParagraphStyle(
            "Heading2",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=14,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#334155")
        )
        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748b")
        )

        story = []

        # Title and metadata
        story.append(Paragraph(report_data.get("title", "Informe de Inteligencia de Mercado"), title_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"Fecha de corte: {report_data.get('data_cutoff', datetime.now(timezone.utc).isoformat())} · Generado por Steam Intelligence", subtitle_style))
        story.append(Spacer(1, 14))

        # Executive Summary
        story.append(Paragraph("1. Resumen Ejecutivo", h2_style))
        story.append(Paragraph(report_data.get("summary", "Sin resumen disponible."), body_style))
        story.append(Spacer(1, 12))

        # Key Findings
        story.append(Paragraph("2. Hallazgos Cuantitativos y Evidencias", h2_style))
        findings = report_data.get("findings", [])
        if findings:
            table_data = [["Afirmación / Hallazgo", "Métrica", "Confianza"]]
            for f in findings:
                table_data.append([
                    Paragraph(f.get("claim", ""), body_style),
                    f.get("metric", "N/A"),
                    f.get("confidence", "N/A").upper()
                ])
            t = Table(table_data, colWidths=[330, 110, 64])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
            ]))
            story.append(t)
        else:
            story.append(Paragraph("No se registraron hallazgos específicos.", body_style))

        story.append(Spacer(1, 14))

        # Recommendations
        story.append(Paragraph("3. Recomendaciones Tácticas", h2_style))
        recommendations = report_data.get("recommendations", [])
        for r in recommendations:
            story.append(Paragraph(f"• {r}", body_style))
        story.append(Spacer(1, 12))

        # Limitations & Methodological Disclaimer
        story.append(Paragraph("4. Limitaciones y Fuentes de Datos", h2_style))
        limitations = report_data.get("limitations", [])
        for lim in limitations:
            story.append(Paragraph(f"• {lim}", disclaimer_style))

        story.append(Spacer(1, 8))
        story.append(Paragraph(
            "Nota metodológica: Steam Intelligence recopila telemetría de fuentes oficiales públicas y terceras partes autorizadas. La asociación temporal de métricas no implica causalidad de ventas.",
            disclaimer_style
        ))

        doc.build(story, canvasmaker=NumberedCanvas)
        return filepath

    @staticmethod
    def generate_pptx_export(report_data: Dict[str, Any], filename: str) -> str:
        """Generates 16:9 widescreen presentation deck with dark theme."""
        filepath = os.path.join(EXPORTS_DIR, filename)
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        blank_slide_layout = prs.slide_layouts[6]

        def set_dark_background(slide):
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(14, 20, 34)  # Deep graphite / dark navy

        # Slide 1: Title Slide
        s1 = prs.slides.add_slide(blank_slide_layout)
        set_dark_background(s1)

        txBox = s1.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.3), Inches(3.0))
        tf = txBox.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = report_data.get("title", "STEAM INTELLIGENCE REPORT")
        p1.font.bold = True
        p1.font.size = Pt(36)
        p1.font.color.rgb = RGBColor(255, 255, 255)

        p2 = tf.add_paragraph()
        p2.text = f"Análisis de mercado, demanda y competencia · Corte: {report_data.get('data_cutoff', '2026')}"
        p2.font.size = Pt(16)
        p2.font.color.rgb = RGBColor(56, 189, 248)  # Cyan accent

        # Slide 2: Executive Summary
        s2 = prs.slides.add_slide(blank_slide_layout)
        set_dark_background(s2)

        title_box = s2.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(0.8))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = "Executive Summary"
        p.font.bold = True
        p.font.size = Pt(28)
        p.font.color.rgb = RGBColor(255, 255, 255)

        content_box = s2.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.5))
        tf_c = content_box.text_frame
        tf_c.word_wrap = True

        p_sum = tf_c.paragraphs[0]
        p_sum.text = report_data.get("summary", "Sin resumen disponible.")
        p_sum.font.size = Pt(16)
        p_sum.font.color.rgb = RGBColor(226, 232, 240)

        # Bullets for findings
        for f in report_data.get("findings", [])[:3]:
            p_bullet = tf_c.add_paragraph()
            p_bullet.text = f"• {f.get('claim', '')} (Confianza: {f.get('confidence', '').upper()})"
            p_bullet.font.size = Pt(14)
            p_bullet.font.color.rgb = RGBColor(148, 163, 184)

        # Slide 3: Recommendations & Limitations
        s3 = prs.slides.add_slide(blank_slide_layout)
        set_dark_background(s3)

        title_box = s3.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(0.8))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = "Strategic Recommendations & Limitations"
        p.font.bold = True
        p.font.size = Pt(28)
        p.font.color.rgb = RGBColor(255, 255, 255)

        content_box = s3.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.8))
        tf_c = content_box.text_frame
        tf_c.word_wrap = True

        p_rec_h = tf_c.paragraphs[0]
        p_rec_h.text = "Recomendaciones:"
        p_rec_h.font.bold = True
        p_rec_h.font.size = Pt(18)
        p_rec_h.font.color.rgb = RGBColor(56, 189, 248)

        for r in report_data.get("recommendations", [])[:4]:
            p_bullet = tf_c.add_paragraph()
            p_bullet.text = f"• {r}"
            p_bullet.font.size = Pt(13)
            p_bullet.font.color.rgb = RGBColor(226, 232, 240)

        p_lim_h = tf_c.add_paragraph()
        p_lim_h.text = "\nLimitaciones de Datos:"
        p_lim_h.font.bold = True
        p_lim_h.font.size = Pt(16)
        p_lim_h.font.color.rgb = RGBColor(251, 146, 60)

        for l in report_data.get("limitations", [])[:3]:
            p_bullet = tf_c.add_paragraph()
            p_bullet.text = f"• {l}"
            p_bullet.font.size = Pt(12)
            p_bullet.font.color.rgb = RGBColor(148, 163, 184)

        prs.save(filepath)
        return filepath
