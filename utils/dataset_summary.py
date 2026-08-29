import os
import pandas as pd

from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GENERATE DATASET SUMMARY
# ============================================================

def generate_dataset_summary(
    df,
    profile=None,
    quality=None
):

    # ========================================================
    # CHECK API KEY
    # ========================================================

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:

        raise ValueError(
            "GEMINI_API_KEY was not found. "
            "Please add it to your .env file."
        )


    # ========================================================
    # CREATE GEMINI CLIENT
    # ========================================================

    client = genai.Client(
        api_key=api_key
    )


    # ========================================================
    # BASIC INFORMATION
    # ========================================================

    rows = len(df)

    columns = len(df.columns)

    column_names = df.columns.tolist()


    # ========================================================
    # NUMERICAL COLUMNS
    # ========================================================

    numerical_columns = (
        df
        .select_dtypes(
            include="number"
        )
        .columns
        .tolist()
    )


    # ========================================================
    # CATEGORICAL COLUMNS
    # ========================================================

    categorical_columns = (
        df
        .select_dtypes(
            include=["object", "category"]
        )
        .columns
        .tolist()
    )


    # ========================================================
    # MISSING VALUES
    # ========================================================

    missing_values = int(
        df.isnull().sum().sum()
    )


    # ========================================================
    # DUPLICATE ROWS
    # ========================================================

    duplicate_rows = int(
        df.duplicated().sum()
    )


    # ========================================================
    # NUMERICAL STATISTICS
    # ========================================================

    numerical_summary = {}

    for column in numerical_columns:

        series = df[column].dropna()

        if series.empty:
            continue

        numerical_summary[column] = {

            "mean": round(
                float(series.mean()),
                2
            ),

            "median": round(
                float(series.median()),
                2
            ),

            "minimum": round(
                float(series.min()),
                2
            ),

            "maximum": round(
                float(series.max()),
                2
            ),

            "total": round(
                float(series.sum()),
                2
            )
        }


    # ========================================================
    # PROFILE INFORMATION
    # ========================================================

    profile_text = ""

    if profile:

        profile_text = f"""
DATASET PROFILE

Rows:
{profile.get("rows", rows)}

Columns:
{profile.get("columns", columns)}

Numerical columns:
{profile.get("numerical_columns", [])}

Categorical columns:
{profile.get("categorical_columns", [])}

Date columns:
{profile.get("date_columns", [])}
"""


    # ========================================================
    # DATA QUALITY INFORMATION
    # ========================================================

    quality_text = ""

    if quality:

        quality_text = f"""
DATA QUALITY

Missing values:
{quality.get("missing_values", {})}

Duplicate rows:
{quality.get("duplicate_rows", 0)}

Duplicate Order IDs:
{quality.get("duplicate_order_ids", 0)}

Negative values:
{quality.get("negative_values", {})}

Zero values:
{quality.get("zero_values", {})}

Invalid dates:
{quality.get("invalid_dates", {})}
"""


    # ========================================================
    # DATA SAMPLE
    # ========================================================

    sample = df.head(10).to_string(
        index=False
    )


    # ========================================================
    # GEMINI PROMPT
    # ========================================================

    prompt = f"""
You are an expert data analyst.

Analyze the following dataset information and create
a concise, accurate, business-friendly summary.

DATASET INFORMATION

Rows:
{rows}

Columns:
{columns}

Column names:
{column_names}

Numerical columns:
{numerical_columns}

Categorical columns:
{categorical_columns}

Missing values:
{missing_values}

Duplicate rows:
{duplicate_rows}

Numerical statistics:
{numerical_summary}

{profile_text}

{quality_text}

SAMPLE DATA

{sample}


Your response MUST contain exactly these sections:

1. Dataset Overview
2. Data Quality
3. Numerical Insights
4. Key Business Observations

Rules:

- Use actual numbers from the dataset.
- Do not invent information.
- Keep the explanation easy to understand.
- Highlight useful business patterns.
- Do not make unsupported conclusions.
- If there is insufficient information, clearly say so.
- Keep the response concise.
"""


    # ========================================================
    # GEMINI API CALL
    # ========================================================

    response = client.models.generate_content(

        model="gemini-3.6-flash",

        contents=prompt

    )


    # ========================================================
    # RETURN ANSWER
    # ========================================================

    return response.text.strip()