import os
import json
import pandas as pd
from pypdf import PdfReader
from docx import Document


def extract_text(file_path):
    """
    Extract text/data from different file types.
    """

    extension = os.path.splitext(file_path)[1].lower()

    # PDF
    if extension == ".pdf":
        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    # TXT
    elif extension == ".txt":
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    # CSV
    elif extension == ".csv":
        df = pd.read_csv(file_path)
        return df.to_string(index=False)

    # Excel
    elif extension in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
        return df.to_string(index=False)

    # JSON
    elif extension == ".json":
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return json.dumps(data, indent=2)

    # DOCX
    elif extension == ".docx":
        document = Document(file_path)

        text = ""

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

        return text

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )