
import os
import pandas as pd
from dotenv import load_dotenv
from google import genai
from web_search import search_web
import time

# Load API key from .env
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_data(df):
    """
    Analyze the uploaded DataFrame using Python/Pandas.
    """

    analysis = {}

    # -----------------------------
    # 1. Basic dataset information
    # -----------------------------

    analysis["total_records"] = len(df)
    analysis["total_columns"] = len(df.columns)
    analysis["columns"] = df.columns.tolist()

    # -----------------------------
    # 2. Missing values
    # -----------------------------

    missing_values = df.isnull().sum()

    analysis["missing_values"] = {
        column: int(value)
        for column, value in missing_values.items()
        if value > 0
    }

    # -----------------------------
    # 3. Numerical columns
    # -----------------------------

    numerical_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    analysis["numerical_columns"] = numerical_columns

    # -----------------------------
    # 4. Numerical statistics
    # -----------------------------

    numerical_statistics = {}

    for column in numerical_columns:

        numerical_statistics[column] = {
            "mean": float(df[column].mean()),
            "median": float(df[column].median()),
            "minimum": float(df[column].min()),
            "maximum": float(df[column].max()),
            "sum": float(df[column].sum())
        }

    analysis["numerical_statistics"] = numerical_statistics

    # -----------------------------
    # 5. Categorical columns
    # -----------------------------

    categorical_columns = df.select_dtypes(
    include=["object", "string", "category"]
    ).columns.tolist()

    analysis["categorical_columns"] = categorical_columns

    # -----------------------------
    # 6. Categorical information
    # -----------------------------

    categorical_statistics = {}

    for column in categorical_columns:

        categorical_statistics[column] = {
            "unique_values": int(df[column].nunique()),
            "top_values": df[column]
            .value_counts()
            .head(10)
            .to_dict()
        }

    analysis["categorical_statistics"] = categorical_statistics

    # -----------------------------
    # 7. Correlation analysis
    # -----------------------------

    if len(numerical_columns) >= 2:

        correlation = df[numerical_columns].corr()

        analysis["correlations"] = correlation.round(3).to_dict()

    else:

        analysis["correlations"] = {}

    return analysis


def get_web_research(df):
    """
    Generate a simple research query from the dataset
    and collect relevant information from the web.
    """

    columns = ", ".join(df.columns.tolist())

    query = f"""
    Business analysis and industry context related to:
    {columns}
    Explain important industry trends, benchmarks,
    and general factors relevant to analyzing these variables.
    """

    try:
        results = search_web(query)
        return results
    except Exception as e:
        return f"Web search failed: {str(e)}"


def generate_report(df):
    analysis = analyze_data(df)
    analysis_text = str(analysis)

    web_research = get_web_research(df)
    web_research_text = str(web_research)

    prompt = f"""
You are a professional business data analyst and report writer.

IMPORTANT RULES:

1. Use the provided analysis as the factual basis of the report.
2. Do not invent numbers, statistics, trends, companies, markets,
   or facts that are not supported by the provided information.
3. Clearly distinguish between factual findings, interpretation,
   and limitations.
4. Use web research only for external context.
5. Do not present web research as if it came from the uploaded dataset.
6. Do not invent facts or statistics.

DATA ANALYSIS:

{analysis_text}

WEB RESEARCH:

{web_research_text}

Prepare the following sections:

1. Executive Summary
2. Introduction
3. Objectives
4. Dataset Description
5. Data Quality Analysis
6. Descriptive Statistics
7. Numerical Variable Analysis
8. Categorical Variable Analysis
9. Correlation Analysis
10. Key Findings
11. Business Interpretation
12. Limitations
13. Conclusion
"""

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )
            break

        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(
                    f"Gemini temporarily unavailable. "
                    f"Retrying in {wait_time} seconds..."
                )
                time.sleep(wait_time)
            else:
                raise

    return {
        "analysis": analysis,
        "generated_report": response.text
    }

# ---------------------------------
# TEST THE REPORT GENERATOR
# ---------------------------------

if __name__ == "__main__":

    test_data = pd.DataFrame({
        "Product": ["A", "B", "C"],
        "Revenue": [1000, 2000, 1500],
        "Quantity": [10, 20, 15]
    })

    result = generate_report(test_data)

    print(result["generated_report"])

