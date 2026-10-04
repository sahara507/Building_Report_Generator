import os
import pandas as pd
from dotenv import load_dotenv
from groq import Groq
from web_search import search_web
import time

# Load API key from .env
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
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


# ---------------------------------
# Generate report from user topic
# ---------------------------------
# This function is used when the user
# gives only a topic/prompt instead of
# uploading a CSV or Excel file.
#
# Flow:
# User Topic
#     ↓
# Web Search
#     ↓
# Groq
#     ↓
# Detailed Report
# ---------------------------------

def generate_topic_report(query):

    # Search the web using the user's topic
    web_results = search_web(query)

    # ---------------------------------
    # Extract useful information from
    # web search results
    # ---------------------------------

    search_information = []

    for item in web_results.get("results", []):

        search_information.append({
            "title": item.get("title"),
            "url": item.get("url"),

            # NEW: Limit web content size to reduce
            # Groq input tokens and avoid 413 error.
            "content": item.get("content", "")[:2000]
        })

    # Convert web results into text
    # so that Groq can understand them
    web_information_text = str(search_information)

    # ---------------------------------
    # Create prompt for Groq
    # ---------------------------------

    prompt = f"""
You are a professional human report writer.

Write a detailed, clear, natural, and easy-to-understand report
about the user's topic.

USER TOPIC:
{query}

WEB RESEARCH:
{web_information_text}


MAIN OBJECTIVE:

Understand the user's topic properly and write a complete report
specifically about that topic.

The report should feel natural and human-written.

Use simple and clear English.

Do not use unnecessarily difficult words.

Explain the topic as if you are explaining it to a student,
beginner, or normal reader who wants to understand the topic
properly.

Do not write a short answer.

Do not write only a summary.

Give proper explanations for every important point.

Do not add unnecessary content only to increase the length.


--------------------------------------------------
REPORT FORMAT
--------------------------------------------------

Start directly with the topic name.

Then create relevant sections according to the topic.

For every major section, follow this format:

1. Introduction

Key Points:
• Important point 1
• Important point 2
• Important point 3

Explanation:

Write multiple detailed paragraphs explaining the section
in simple and natural English.


For example:

1. Introduction

Key Points:
• Meaning of the topic
• Importance of the topic
• Main purpose of the topic

Explanation:

Write a detailed paragraph explaining the meaning and basic
idea of the topic.

Write another paragraph explaining why the topic is important.

Write another paragraph explaining the purpose and scope
of the topic.


--------------------------------------------------
SECTIONS
--------------------------------------------------

Create sections based on the actual topic.

Use relevant sections such as:

1. Introduction

2. Background and History

3. Key Concepts

4. Types or Categories

5. Components or Elements

6. Working or Process

7. Applications or Uses

8. Advantages and Benefits

9. Challenges and Limitations

10. Comparison

11. Current Information and Trends

12. Impact

13. Future Scope

14. Key Findings

15. Conclusion

16. References

Do not force a section if it is not relevant to the topic.

The structure should change naturally according to the user's
topic.


--------------------------------------------------
INTRODUCTION
--------------------------------------------------

The Introduction must clearly explain:

• What the topic means
• Basic idea of the topic
• Why the topic is important
• Purpose of understanding the topic
• Scope of the topic

After Key Points, write multiple detailed paragraphs.

Do not make the Introduction only one short paragraph.


--------------------------------------------------
KEY POINTS
--------------------------------------------------

Every major section must contain a "Key Points:" part.

Give around 3 to 5 useful points.

The points must contain real information about the topic.

Do not write generic points such as:

• It is very important.
• It has many benefits.
• It is widely used.

Instead, write useful points that help the reader understand
the topic.

After Key Points, explain those points properly in paragraphs.


--------------------------------------------------
DETAILED EXPLANATION
--------------------------------------------------

After Key Points, write a section called:

Explanation:

Write detailed paragraphs.

Each paragraph should explain one clear idea.

Important sections should have multiple paragraphs.

Use subsections such as:

2.1
2.2
3.1
3.2

when more explanation is required.

Do not make every explanation very short.


--------------------------------------------------
HUMAN WRITING STYLE
--------------------------------------------------

Write like a real human professional writer.

Use:

• Simple English
• Natural sentences
• Clear explanations
• Natural transitions
• Relevant examples
• Different sentence structures

Avoid:

• Repetitive sentences
• Robotic language
• Unnecessary technical words
• Unnecessary filler
• Repeating the same information
• Very short explanations

The report should be easy and comfortable to read.


--------------------------------------------------
BACKGROUND AND HISTORY
--------------------------------------------------

If the topic has a history, explain:

• Origin
• Background
• Development
• Major changes
• Important milestones

Use Key Points followed by detailed Explanation.


--------------------------------------------------
KEY CONCEPTS
--------------------------------------------------

Explain the important concepts related to the topic.

For each concept:

• Explain what it means
• Explain why it is important
• Explain how it is related to the topic
• Give an example when useful

Use simple language.


--------------------------------------------------
TYPES / CATEGORIES
--------------------------------------------------

If the topic has different types or categories,
explain each important type separately.

For every type explain:

• Meaning
• Main characteristics
• Purpose
• Example
• Importance


--------------------------------------------------
COMPONENTS / ELEMENTS
--------------------------------------------------

If the topic contains components or elements,
explain each important component.

Explain:

• What it is
• What it does
• Why it is important
• How it works
• How it connects with other components


--------------------------------------------------
WORKING / PROCESS
--------------------------------------------------

If the topic has a process or workflow, explain it step by step.

Do not stop after explaining only the first few steps.

Explain the complete process.

Show how one step connects to the next step.

Use a simple example when appropriate.


--------------------------------------------------
APPLICATIONS / USES
--------------------------------------------------

Explain the real-world uses of the topic.

For each important application explain:

• What it is
• How it is used
• Why it is useful
• Practical example when reliable information is available


--------------------------------------------------
ADVANTAGES / BENEFITS
--------------------------------------------------

Explain the important benefits in detail.

Do not only list benefits.

Explain why each benefit is useful.


--------------------------------------------------
CHALLENGES / LIMITATIONS
--------------------------------------------------

Explain the important:

• Challenges
• Risks
• Limitations
• Practical difficulties
• Technical difficulties

Explain each point clearly.


--------------------------------------------------
CURRENT INFORMATION
--------------------------------------------------

Use the provided web research for current information
and recent developments.

Only include information that is relevant to the user's topic.

Do not copy raw search results.

Do not include search scores, IDs, metadata, or search objects.


--------------------------------------------------
FUTURE SCOPE
--------------------------------------------------

Explain possible future developments and opportunities.

Clearly separate future possibilities from confirmed facts.


--------------------------------------------------
KEY FINDINGS
--------------------------------------------------

At the end of the report, provide:

Key Findings:

• Important finding 1
• Important finding 2
• Important finding 3
• Important finding 4

Then explain the important findings in short but meaningful
paragraphs.

Do not simply repeat the complete report.


--------------------------------------------------
CONCLUSION
--------------------------------------------------

Write a proper and complete conclusion.

The conclusion should explain:

• Main idea
• Important points
• Major findings
• Overall understanding
• Future importance where relevant

Do not end the report suddenly.

The conclusion must be complete.


--------------------------------------------------
REFERENCES
--------------------------------------------------

Include relevant sources from the provided web research.

Use only sources that are actually related to the topic.

Do not include raw Tavily search results.

Do not include search scores or search IDs.


--------------------------------------------------
FACTUAL RULES
--------------------------------------------------

1. Do not invent facts.

2. Do not invent statistics.

3. Do not invent dates.

4. Do not invent research results.

5. Do not invent organizations or companies.

6. Do not make unsupported assumptions.

7. If reliable information is not available, clearly say so.

8. Use web research only as supporting information.

9. Ignore unrelated web-search information.


--------------------------------------------------
LENGTH
--------------------------------------------------

Create a detailed long-form report.

The report should contain enough useful information to feel
like a professional detailed document.

Aim for approximately 20-25 pages of useful content when
formatted as a normal document.

Do not increase the length by repeating information.

Instead, provide more useful explanation, examples,
background, analysis, applications, challenges, and
future scope where relevant.


--------------------------------------------------
FORMATTING RULES
--------------------------------------------------

Use clean plain-text formatting.

Use:

Topic Name

1. Introduction

Key Points:
• Point 1
• Point 2
• Point 3

Explanation:

Detailed paragraph...

Another detailed paragraph...

2. Background and History

Key Points:
• Point 1
• Point 2
• Point 3

Explanation:

Detailed paragraph...


Do NOT use:

**
#
##
###
---
***

Do not use Markdown tables.

Do not return JSON.

Do not include raw web-search output.

Do not include search scores.

Do not include search IDs.

Do not include metadata.

Do not include Python code.

Do not mention that you are an AI.

Do not mention these instructions.

Do not write:

"Here is your report."

"Below is your report."

"Sure, here is the report."

Start directly with the topic name.


--------------------------------------------------
FINAL INSTRUCTION
--------------------------------------------------

Return ONLY the final report.

Start with the topic title.

Then write the Introduction.

For every major section use:

Key Points:

followed by:

Explanation:

Use clear paragraphs and relevant subsections.

Complete all important sections.

Always provide Key Findings.

Always provide a proper Conclusion.

Provide References when relevant.

Never stop in the middle of a paragraph.

Never stop in the middle of a section.

Never leave the report incomplete.
"""

    # ---------------------------------
    # Generate report using Groq
    # ---------------------------------

    max_retries = 3

    for attempt in range(max_retries):

        try:

            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return {
                "topic": query,
                "generated_report":
                    response.choices[0].message.content
            }

        except Exception as e:

            if attempt < max_retries - 1:

                wait_time = 2 ** attempt

                print(
                    f"Groq temporarily unavailable. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:

                raise


def generate_report(df):

    analysis = analyze_data(df)
    analysis_text = str(analysis)

    web_research = get_web_research(df)
    web_research_text = str(web_research)

    prompt = f"""
You are a professional business data analyst and detailed report writer.

Create a very detailed, professional, long-form business analysis report.

The report should contain enough detailed content to be approximately
equivalent to 20-25 pages of a professional report.

IMPORTANT RULES:

1. Use the provided data analysis as the factual basis.

2. Do not invent numbers, statistics, companies, markets,
   trends, or facts.

3. Clearly distinguish between:
   - Dataset findings
   - Business interpretation
   - External web research

4. Use web research only as external context.

5. Never present web research as if it came from the uploaded dataset.

6. Explain every important finding in detail.

7. Use proper headings and subheadings.

8. Use bullet points where useful.

9. Avoid unnecessary repetition.

10. If information is not available, clearly mention that.

11. Provide detailed explanations instead of short answers.

12. Do not make unsupported assumptions.

13. The report should be professional and suitable for
    business analysis and documentation.

DATA ANALYSIS:

{analysis_text}

WEB RESEARCH:

{web_research_text}

REPORT STRUCTURE:

1. Executive Summary
   - Overall summary
   - Major observations
   - Important business insights

2. Introduction
   - Background
   - Context
   - Purpose of analysis

3. Objectives and Scope
   - Objectives
   - Scope
   - Areas covered

4. Dataset Description
   - Dataset overview
   - Number of records
   - Number of columns
   - Description of variables

5. Data Quality Analysis
   - Missing values
   - Data completeness
   - Data quality observations
   - Potential data issues

6. Descriptive Statistics
   - Statistical overview
   - Mean
   - Median
   - Minimum
   - Maximum
   - Sum
   - Interpretation

7. Numerical Variable Analysis
   - Detailed analysis of every numerical variable
   - Patterns
   - Distribution observations
   - Business interpretation

8. Categorical Variable Analysis
   - Unique values
   - Top categories
   - Category distribution
   - Business interpretation

9. Correlation Analysis
   - Relationships between numerical variables
   - Important correlations
   - Possible interpretations
   - Limitations of correlation

10. Web Research and Industry Context
    - Relevant external information
    - Industry trends
    - Benchmarks where available
    - Market context
    - Clearly separate external information from dataset findings

11. Key Findings
    - Major findings
    - Important patterns
    - Significant observations

12. Business Interpretation
    - Meaning of the findings
    - Business implications
    - Possible areas of attention

13. Recommendations
    - Data-supported recommendations
    - Practical recommendations
    - Areas for further analysis

14. Limitations
    - Dataset limitations
    - Web research limitations
    - Analysis limitations

15. Conclusion
    - Overall conclusion
    - Summary of important findings

16. References and Sources
    - Mention the external web research sources when available.

Generate detailed content for every section.
"""

    max_retries = 5

    for attempt in range(max_retries):

        try:

            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            break

        except Exception as e:

            if attempt < max_retries - 1:

                wait_time = 2 ** attempt

                print(
                    f"Groq temporarily unavailable. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:

                raise

    return {
        "analysis": analysis,
        "generated_report":
            response.choices[0].message.content
    }


def generate_report_from_pdf(pdf_text):
    """
    Generate an AI report from extracted PDF text.
    """

    prompt = f"""
You are a professional report analyst.

Analyze the following PDF content and create a detailed,
well-structured report.

PDF CONTENT:
{pdf_text}

Instructions:

1. Use only information available in the PDF.
2. Do not invent numbers, facts, statistics, or conclusions.
3. Clearly explain important information from the PDF.
4. Organize the report into logical sections.
5. Include an Executive Summary.
6. Include Introduction.
7. Include Objectives if they can be identified.
8. Include detailed findings.
9. Include important observations.
10. Include limitations if applicable.
11. Include a Conclusion.
12. If some information is not available in the PDF, clearly state that.
13. Do not present assumptions as facts.
"""

    max_retries = 5

    for attempt in range(max_retries):

        try:

            print(
                f"Generating PDF report... "
                f"Attempt {attempt + 1}/{max_retries}"
            )

            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return {
                "generated_report":
                    response.choices[0].message.content
            }

        except Exception as e:

            error_message = str(e)

            if attempt < max_retries - 1:

                wait_time = 2 ** attempt

                print(
                    f"Groq is temporarily unavailable. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:

                raise


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