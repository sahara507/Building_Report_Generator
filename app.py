from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse

from ingestion import load_file
from report_generator import generate_report, generate_report_from_pdf
from web_search import search_web

from database import (
    create_database,
    save_original_file,
    save_generated_report
)

import os
import html
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="_BUILDING_REPORT_GENERATOR_",
    description="Generates the reports using Gen_AI",
)


# --------------------------------------------------
# FOLDERS
# --------------------------------------------------

UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "Reports"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)


# Create database
create_database()


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Automated Report Generator is running"
    }


# --------------------------------------------------
# CREATE HTML REPORT
# --------------------------------------------------

def create_html_report(report_text, filename):

    report_name = Path(filename).stem

    html_filename = f"{report_name}_report.html"

    html_path = os.path.join(
        REPORT_FOLDER,
        html_filename
    )

    # Escape HTML characters
    safe_text = html.escape(report_text)

    # Convert simple Markdown headings
    lines = safe_text.split("\n")

    formatted_lines = []

    for line in lines:

        if line.startswith("# "):
            formatted_lines.append(
                f"<h1>{line[2:]}</h1>"
            )

        elif line.startswith("## "):
            formatted_lines.append(
                f"<h2>{line[3:]}</h2>"
            )

        elif line.startswith("### "):
            formatted_lines.append(
                f"<h3>{line[4:]}</h3>"
            )

        elif line.startswith("- "):
            formatted_lines.append(
                f"<li>{line[2:]}</li>"
            )

        else:
            if line.strip():
                formatted_lines.append(
                    f"<p>{line}</p>"
                )

    formatted_report = "\n".join(formatted_lines)

    html_content = f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <title>{html.escape(report_name)}</title>

    <style>

        body {{
            font-family: Arial, sans-serif;
            margin: 50px;
            line-height: 1.6;
            color: #222;
        }}

        h1 {{
            text-align: center;
            margin-bottom: 40px;
        }}

        h2 {{
            margin-top: 35px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 8px;
        }}

        h3 {{
            margin-top: 25px;
        }}

        p {{
            text-align: justify;
        }}

        li {{
            margin-bottom: 8px;
        }}

    </style>

</head>

<body>

    {formatted_report}

</body>

</html>
"""

    with open(
        html_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(html_content)

    return html_filename


# --------------------------------------------------
# CREATE PDF REPORT
# --------------------------------------------------

def create_pdf_report(report_text, filename):

    report_name = Path(filename).stem
    pdf_filename = f"{report_name}_report.pdf"
    pdf_path = os.path.join(REPORT_FOLDER, pdf_filename)

    document = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=60,
        bottomMargin=60
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=24,
        leading=30,
        spaceAfter=30
    )

    heading1_style = ParagraphStyle(
        "Heading1Custom",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        spaceBefore=20,
        spaceAfter=12
    )

    heading2_style = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontSize=15,
        leading=19,
        spaceBefore=18,
        spaceAfter=10
    )

    heading3_style = ParagraphStyle(
        "Heading3Custom",
        parent=styles["Heading3"],
        fontSize=13,
        leading=17,
        spaceBefore=14,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontSize=10.5,
        leading=16,
        spaceAfter=9,
        alignment=4
    )

    bullet_style = ParagraphStyle(
        "BulletCustom",
        parent=body_style,
        leftIndent=18,
        firstLineIndent=-10,
        spaceAfter=6
    )

    story = []

    # ------------------------------------------------
    # COVER PAGE
    # ------------------------------------------------

    story.append(Spacer(1, 1.5 * inch))

    story.append(
        Paragraph(
            "AUTOMATED AI REPORT",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Generated Report",
            heading2_style
        )
    )

    story.append(Spacer(1, 30))

    story.append(
        Paragraph(
            html.escape(report_name),
            heading1_style
        )
    )

    story.append(Spacer(1, 40))

    story.append(
        Paragraph(
            "Generated using Artificial Intelligence",
            body_style
        )
    )

    story.append(
        Paragraph(
            "AI Report Generator",
            body_style
        )
    )

    story.append(PageBreak())

    # ------------------------------------------------
    # REPORT CONTENT
    # ------------------------------------------------

    lines = report_text.split("\n")

    for line in lines:

        line = line.strip()

        if not line:
            story.append(Spacer(1, 6))
            continue

        # Main heading
        if line.startswith("# "):

            text = html.escape(line[2:])

            story.append(
                Paragraph(
                    text,
                    heading1_style
                )
            )

        # Section heading
        elif line.startswith("## "):

            text = html.escape(line[3:])

            story.append(
                Paragraph(
                    text,
                    heading2_style
                )
            )

        # Subsection heading
        elif line.startswith("### "):

            text = html.escape(line[4:])

            story.append(
                Paragraph(
                    text,
                    heading3_style
                )
            )

        # Bullet points
        elif line.startswith("- "):

            text = html.escape(line[2:])

            story.append(
                Paragraph(
                    "• " + text,
                    bullet_style
                )
            )

        # Numbered points
        elif (
            len(line) > 2
            and line[0].isdigit()
            and ". " in line[:4]
        ):

            text = html.escape(line)

            story.append(
                Paragraph(
                    text,
                    body_style
                )
            )

        # Markdown table
        elif line.startswith("|"):

            # Skip markdown separator rows
            if "---" in line:
                continue

            cells = [
                cell.strip()
                for cell in line.strip("|").split("|")
            ]

            table_data = [
                [Paragraph(html.escape(cell), body_style)
                 for cell in cells]
            ]

            table = Table(
                table_data,
                repeatRows=1,
                hAlign="LEFT"
            )

            table.setStyle(
                TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ])
            )

            story.append(table)
            story.append(Spacer(1, 10))

        # Normal paragraph
        else:

            text = html.escape(line)

            story.append(
                Paragraph(
                    text,
                    body_style
                )
            )

    # ------------------------------------------------
    # HEADER + FOOTER
    # ------------------------------------------------

    def add_page_number(canvas, doc):

        canvas.saveState()

        canvas.setFont("Helvetica", 8)

        canvas.drawString(
            50,
            30,
            "AI Report Generator"
        )

        canvas.drawRightString(
            A4[0] - 50,
            30,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    return pdf_filename


# --------------------------------------------------
# UPLOAD FILE
# --------------------------------------------------

@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    filename = file.filename

    extension = Path(filename).suffix.lower()

    allowed_extensions = (
        ".csv",
        ".xlsx",
        ".pdf"
    )

    if extension not in allowed_extensions:

        return {
            "error":
            "Only CSV, Excel (.xlsx), and PDF files are supported."
        }


    # --------------------------------------------------
    # SAVE ORIGINAL FILE
    # --------------------------------------------------

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        content = await file.read()

        buffer.write(content)


    # --------------------------------------------------
    # SAVE FILE INFORMATION IN DATABASE
    # --------------------------------------------------

    file_id = save_original_file(filename)


    # --------------------------------------------------
    # LOAD FILE
    # --------------------------------------------------

    data = load_file(file_path)


    # --------------------------------------------------
    # GENERATE AI REPORT
    # --------------------------------------------------

    if extension in (".csv", ".xlsx"):

        result = generate_report(data)

        report_text = result["generated_report"]

        response_data = {
            "records": len(data),
            "columns": data.columns.tolist()
        }

    else:

        result = generate_report_from_pdf(data)

        report_text = result["generated_report"]

        response_data = {
            "extracted_text_length": len(data)
        }


    # --------------------------------------------------
    # CREATE HTML REPORT
    # --------------------------------------------------

    html_filename = create_html_report(
        report_text,
        filename
    )


    # --------------------------------------------------
    # CREATE PDF REPORT
    # --------------------------------------------------

    pdf_filename = create_pdf_report(
        report_text,
        filename
    )


    # --------------------------------------------------
    # SAVE GENERATED REPORT IN DATABASE
    # --------------------------------------------------

    save_generated_report(
        file_id,
        pdf_filename
    )


    # --------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------

    return {

        "filename": filename,

        "file_type": extension,

        "message":
        "File uploaded and report generated successfully",

        "html_report":
        f"/download/html/{html_filename}",

        "pdf_report":
        f"/download/pdf/{pdf_filename}",

        **response_data
    }


# --------------------------------------------------
# DOWNLOAD PDF
# --------------------------------------------------

@app.get("/download/pdf/{filename}")
def download_pdf(filename: str):

    file_path = os.path.join(
        REPORT_FOLDER,
        filename
    )

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename
    )


# --------------------------------------------------
# DOWNLOAD HTML
# --------------------------------------------------

@app.get("/download/html/{filename}")
def download_html(filename: str):

    file_path = os.path.join(
        REPORT_FOLDER,
        filename
    )

    return FileResponse(
        file_path,
        media_type="text/html",
        filename=filename
    )


# --------------------------------------------------
# TAVILY WEB SEARCH
# --------------------------------------------------

@app.get("/web-search")
def web_search(query: str):

    results = search_web(query)

    return {
        "query": query,
        "results": results
    }