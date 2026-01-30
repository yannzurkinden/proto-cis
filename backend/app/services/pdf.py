"""PDF generation service for reports."""

import logging
from datetime import date, datetime
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logger = logging.getLogger(__name__)

# -- Colour palette ----------------------------------------------------------
CIS_DARK_BLUE = colors.HexColor("#1e3a5f")
CIS_BLUE = colors.HexColor("#2563eb")
CIS_LIGHT_GREY = colors.HexColor("#f4f6f9")
CIS_BORDER = colors.HexColor("#d1d5db")
CIS_TEXT = colors.HexColor("#333333")
CIS_MUTED = colors.HexColor("#666666")


class PDFService:
    """Service for generating professional PDF reports."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._register_custom_styles()

    # -- Custom styles --------------------------------------------------------

    def _register_custom_styles(self) -> None:
        """Register CIS-branded paragraph styles."""
        self.styles.add(
            ParagraphStyle(
                "CISTitle",
                parent=self.styles["Title"],
                fontSize=18,
                textColor=CIS_DARK_BLUE,
                spaceAfter=6 * mm,
                leading=22,
            )
        )
        self.styles.add(
            ParagraphStyle(
                "CISHeading",
                parent=self.styles["Heading2"],
                fontSize=13,
                textColor=CIS_DARK_BLUE,
                spaceBefore=6 * mm,
                spaceAfter=3 * mm,
                leading=16,
            )
        )
        self.styles.add(
            ParagraphStyle(
                "CISBody",
                parent=self.styles["BodyText"],
                fontSize=10,
                textColor=CIS_TEXT,
                leading=14,
            )
        )
        self.styles.add(
            ParagraphStyle(
                "CISSmall",
                parent=self.styles["BodyText"],
                fontSize=8,
                textColor=CIS_MUTED,
                leading=10,
            )
        )

    # -- Public API -----------------------------------------------------------

    def generate_beneficiary_summary(self, data: dict) -> bytes:
        """Generate a beneficiary summary PDF.

        Expected *data* keys:
            - beneficiary: dict with nom, prenom, date_naissance, numero_ai,
              unite, msp_referent
            - objectives: list[dict] with titre, statut, progression,
              date_echeance
            - journal_entries: list[dict] with date, auteur, contenu
            - skills: list[dict] with competence, niveau, date_evaluation
            - absences: list[dict] with date_debut, date_fin, motif, justifie
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2.5 * cm,
        )

        story: list[Any] = []
        ben = data.get("beneficiary", {})
        full_name = f"{ben.get('prenom', '')} {ben.get('nom', '')}".strip()
        title = f"Fiche de synthese - {full_name}" if full_name else "Fiche de synthese"
        self._build_header(story, title)

        # -- Informations personnelles ----------------------------------------
        story.append(Paragraph("Informations personnelles", self.styles["CISHeading"]))
        info_data = [
            ["Nom", ben.get("nom", "-")],
            ["Prenom", ben.get("prenom", "-")],
            ["Date de naissance", ben.get("date_naissance", "-")],
            ["Numero AI", ben.get("numero_ai", "-")],
            ["Unite", ben.get("unite", "-")],
            ["MSP referent", ben.get("msp_referent", "-")],
        ]
        story.append(self._make_key_value_table(info_data))
        story.append(Spacer(1, 6 * mm))

        # -- Objectifs PAI ----------------------------------------------------
        objectives = data.get("objectives", [])
        if objectives:
            story.append(Paragraph("Objectifs du PAI", self.styles["CISHeading"]))
            obj_header = ["Objectif", "Statut", "Progression", "Echeance"]
            obj_rows = [obj_header] + [
                [
                    obj.get("titre", "-"),
                    obj.get("statut", "-"),
                    f"{obj.get('progression', 0)} %",
                    obj.get("date_echeance", "-"),
                ]
                for obj in objectives
            ]
            story.append(self._make_data_table(obj_rows))
            story.append(Spacer(1, 6 * mm))

        # -- Competences ------------------------------------------------------
        skills = data.get("skills", [])
        if skills:
            story.append(Paragraph("Competences evaluees", self.styles["CISHeading"]))
            sk_header = ["Competence", "Niveau", "Date evaluation"]
            sk_rows = [sk_header] + [
                [
                    sk.get("competence", "-"),
                    sk.get("niveau", "-"),
                    sk.get("date_evaluation", "-"),
                ]
                for sk in skills
            ]
            story.append(self._make_data_table(sk_rows))
            story.append(Spacer(1, 6 * mm))

        # -- Absences ---------------------------------------------------------
        absences = data.get("absences", [])
        if absences:
            story.append(Paragraph("Absences", self.styles["CISHeading"]))
            ab_header = ["Debut", "Fin", "Motif", "Justifie"]
            ab_rows = [ab_header] + [
                [
                    ab.get("date_debut", "-"),
                    ab.get("date_fin", "-"),
                    ab.get("motif", "-"),
                    "Oui" if ab.get("justifie") else "Non",
                ]
                for ab in absences
            ]
            story.append(self._make_data_table(ab_rows))
            story.append(Spacer(1, 6 * mm))

        # -- Journal ----------------------------------------------------------
        journal = data.get("journal_entries", [])
        if journal:
            story.append(Paragraph("Dernieres entrees du journal", self.styles["CISHeading"]))
            for entry in journal[:10]:  # limit to last 10
                entry_date = entry.get("date", "-")
                auteur = entry.get("auteur", "-")
                contenu = entry.get("contenu", "")
                story.append(
                    Paragraph(
                        f"<b>{entry_date} - {auteur}</b>",
                        self.styles["CISBody"],
                    )
                )
                story.append(Paragraph(contenu, self.styles["CISBody"]))
                story.append(Spacer(1, 3 * mm))

        doc.build(story, onLaterPages=self._build_footer, onFirstPage=self._build_footer)
        return buffer.getvalue()

    def generate_activity_report(
        self, data: dict, date_from: date, date_to: date
    ) -> bytes:
        """Generate an activity report PDF for a given period.

        Expected *data* keys:
            - title: str (optional, defaults to "Rapport d'activite")
            - unite: str
            - total_beneficiaries: int
            - new_beneficiaries: int
            - ended_beneficiaries: int
            - objectives_summary: list[dict] with statut, count
            - absences_summary: dict with total, justified, unjustified
            - entries: list[dict] with date, beneficiaire, type, description
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2.5 * cm,
        )

        story: list[Any] = []
        report_title = data.get("title", "Rapport d'activite")
        self._build_header(story, report_title)

        # -- Periode ----------------------------------------------------------
        period_str = (
            f"Periode : du {date_from.strftime('%d.%m.%Y')} "
            f"au {date_to.strftime('%d.%m.%Y')}"
        )
        story.append(Paragraph(period_str, self.styles["CISBody"]))
        unite = data.get("unite")
        if unite:
            story.append(Paragraph(f"Unite : {unite}", self.styles["CISBody"]))
        story.append(Spacer(1, 6 * mm))

        # -- Chiffres cles ---------------------------------------------------
        story.append(Paragraph("Chiffres cles", self.styles["CISHeading"]))
        kpi_data = [
            ["Beneficiaires actifs", str(data.get("total_beneficiaries", 0))],
            ["Nouveaux beneficiaires", str(data.get("new_beneficiaries", 0))],
            ["Fins d'accompagnement", str(data.get("ended_beneficiaries", 0))],
        ]
        story.append(self._make_key_value_table(kpi_data))
        story.append(Spacer(1, 6 * mm))

        # -- Objectifs --------------------------------------------------------
        obj_summary = data.get("objectives_summary", [])
        if obj_summary:
            story.append(Paragraph("Synthese des objectifs", self.styles["CISHeading"]))
            obj_header = ["Statut", "Nombre"]
            obj_rows = [obj_header] + [
                [o.get("statut", "-"), str(o.get("count", 0))]
                for o in obj_summary
            ]
            story.append(self._make_data_table(obj_rows))
            story.append(Spacer(1, 6 * mm))

        # -- Absences ---------------------------------------------------------
        abs_summary = data.get("absences_summary", {})
        if abs_summary:
            story.append(Paragraph("Absences", self.styles["CISHeading"]))
            abs_data = [
                ["Total absences", str(abs_summary.get("total", 0))],
                ["Justifiees", str(abs_summary.get("justified", 0))],
                ["Non justifiees", str(abs_summary.get("unjustified", 0))],
            ]
            story.append(self._make_key_value_table(abs_data))
            story.append(Spacer(1, 6 * mm))

        # -- Detail des activites ---------------------------------------------
        entries = data.get("entries", [])
        if entries:
            story.append(Paragraph("Detail des activites", self.styles["CISHeading"]))
            ent_header = ["Date", "Beneficiaire", "Type", "Description"]
            ent_rows = [ent_header] + [
                [
                    e.get("date", "-"),
                    e.get("beneficiaire", "-"),
                    e.get("type", "-"),
                    Paragraph(e.get("description", ""), self.styles["CISSmall"]),
                ]
                for e in entries
            ]
            col_widths = [2.5 * cm, 3.5 * cm, 2.5 * cm, None]
            story.append(self._make_data_table(ent_rows, col_widths=col_widths))

        doc.build(story, onLaterPages=self._build_footer, onFirstPage=self._build_footer)
        return buffer.getvalue()

    # -- Internal helpers -----------------------------------------------------

    def _build_header(self, story: list, title: str) -> None:
        """Add a branded CIS header block to the story.

        Adds the main title, a subtitle line with the generation date, and
        a horizontal separator.
        """
        story.append(Paragraph("CIS - Centre d'Integration Socioprofessionnelle", self.styles["CISSmall"]))
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(title, self.styles["CISTitle"]))
        generation_date = datetime.now().strftime("%d.%m.%Y a %H:%M")
        story.append(
            Paragraph(
                f"Document genere le {generation_date}",
                self.styles["CISSmall"],
            )
        )
        # Horizontal rule
        hr_table = Table(
            [[""]],
            colWidths=[17 * cm],
            rowHeights=[1],
        )
        hr_table.setStyle(
            TableStyle(
                [
                    ("LINEBELOW", (0, 0), (-1, -1), 1, CIS_DARK_BLUE),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        story.append(Spacer(1, 3 * mm))
        story.append(hr_table)
        story.append(Spacer(1, 6 * mm))

    def _build_footer(self, canvas, doc) -> None:
        """Draw page number and CIS branding in the footer area."""
        canvas.saveState()
        page_num = doc.page
        footer_text = f"CIS - Page {page_num}"
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(CIS_MUTED)
        # Centered at the bottom
        canvas.drawCentredString(A4[0] / 2, 1.5 * cm, footer_text)
        canvas.restoreState()

    def _make_key_value_table(
        self, rows: list[list[str]]
    ) -> Table:
        """Build a two-column key/value table with CIS styling.

        Args:
            rows: List of [label, value] pairs.
        """
        styled_rows = [
            [
                Paragraph(f"<b>{row[0]}</b>", self.styles["CISBody"]),
                Paragraph(str(row[1]), self.styles["CISBody"]),
            ]
            for row in rows
        ]
        table = Table(styled_rows, colWidths=[5 * cm, 12 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.5, CIS_BORDER),
                    ("BACKGROUND", (0, 0), (0, -1), CIS_LIGHT_GREY),
                ]
            )
        )
        return table

    def _make_data_table(
        self,
        rows: list[list],
        col_widths: list | None = None,
    ) -> Table:
        """Build a data table with a styled header row.

        Args:
            rows: First row is the header; remaining rows are data.
            col_widths: Optional explicit column widths.
        """
        # Wrap header cells in bold paragraphs
        if rows:
            rows[0] = [
                Paragraph(f"<b>{cell}</b>", self.styles["CISBody"])
                if isinstance(cell, str)
                else cell
                for cell in rows[0]
            ]
        # Wrap non-Paragraph data cells
        for i in range(1, len(rows)):
            rows[i] = [
                Paragraph(str(cell), self.styles["CISSmall"])
                if isinstance(cell, str)
                else cell
                for cell in rows[i]
            ]

        table = Table(rows, colWidths=col_widths, repeatRows=1)
        style_commands = [
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), CIS_DARK_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            # Body
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            # Grid
            ("GRID", (0, 0), (-1, -1), 0.5, CIS_BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            # Alternating row colour
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CIS_LIGHT_GREY]),
        ]
        table.setStyle(TableStyle(style_commands))
        return table
