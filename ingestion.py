import pandas as pd
from pypdf import PdfReader


def load_file(file_path: str):

    # CSV
    if file_path.lower().endswith(".csv"):

        df = pd.read_csv(file_path)

        if df.empty:
            raise ValueError("The uploaded CSV file is empty.")

        return df


    # Excel
    elif file_path.lower().endswith(".xlsx"):

        df = pd.read_excel(file_path)

        if df.empty:
            raise ValueError("The uploaded Excel file is empty.")

        return df


    # PDF
    elif file_path.lower().endswith(".pdf"):

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"


        if not text.strip():
            raise ValueError(
                "No readable text was found in the PDF."
            )

        return text


    else:

        raise ValueError(
            "Only CSV, Excel (.xlsx), and PDF files are supported."
        )