import os
import re

from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GEMINI CLIENT
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    client = None
else:
    client = genai.Client(
        api_key=API_KEY
    )


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# BUILD DATASET SCHEMA
# ============================================================

def build_schema(df):
    """
    Create a schema description from the actual dataframe.
    Gemini uses this to avoid guessing column names.
    """

    schema_lines = []

    for column in df.columns:

        dtype = str(df[column].dtype)

        sample_values = (
            df[column]
            .dropna()
            .head(3)
            .tolist()
        )

        schema_lines.append(
            f"- {column} | "
            f"type: {dtype} | "
            f"sample values: {sample_values}"
        )

    return "\n".join(schema_lines)


# ============================================================
# CLEAN SQL
# ============================================================

def clean_sql(sql):
    """
    Remove Markdown/code formatting and unwanted text.
    """

    if not sql:
        return ""

    sql = sql.strip()

    # Remove ```sql
    sql = re.sub(
        r"```sql",
        "",
        sql,
        flags=re.IGNORECASE
    )

    # Remove ```
    sql = sql.replace(
        "```",
        ""
    )

    sql = sql.strip()

    # If AI returned explanation before SQL,
    # try to extract the SELECT statement.
    match = re.search(
        r"(SELECT\s.+)",
        sql,
        flags=re.IGNORECASE | re.DOTALL
    )

    if match:
        sql = match.group(1).strip()

    # Remove trailing semicolon/newlines
    sql = sql.strip()

    return sql


# ============================================================
# VALIDATE SQL
# ============================================================

def validate_sql(sql):
    """
    Allow only read-only SQL.
    """

    if not sql:
        return False, "SQL query is empty."

    normalized = sql.strip().lower()

    # Must start with SELECT or WITH
    if not (
        normalized.startswith("select")
        or normalized.startswith("with")
    ):
        return (
            False,
            "Only SELECT/WITH queries are allowed."
        )

    forbidden_keywords = [
        "insert ",
        "update ",
        "delete ",
        "drop ",
        "alter ",
        "create ",
        "replace ",
        "truncate ",
        "attach ",
        "detach ",
        "pragma ",
    ]

    for keyword in forbidden_keywords:

        if keyword in normalized:

            return (
                False,
                f"Unsafe SQL keyword detected: {keyword.strip()}"
            )

    return True, ""


# ============================================================
# GENERATE SQL
# ============================================================

def generate_sql(question, df):
    """
    Convert a natural-language question into SQL.
    """

    if client is None:

        raise ValueError(
            "GEMINI_API_KEY is not configured."
        )

    if df is None or df.empty:

        raise ValueError(
            "Dataset is empty."
        )

    schema = build_schema(df)

    prompt = f"""
You are an expert SQL Data Analyst.

Convert the user's natural-language question
into a SQLite SQL query.

DATABASE TABLE:
sales

IMPORTANT RULES:

1. Use ONLY the table named sales.
2. Use ONLY columns present in the schema.
3. Never invent column names.
4. SQLite syntax must be used.
5. Return ONLY SQL.
6. Do not use Markdown.
7. Do not provide explanations.
8. Only generate read-only SELECT queries.
9. Never use INSERT, UPDATE, DELETE, DROP,
   ALTER, CREATE or other modification commands.
10. If the user asks for a total, use SUM().
11. If the user asks for an average, use AVG().
12. If the user asks for the highest value, use MAX().
13. If the user asks for the lowest value, use MIN().
14. If the user asks for number of records, use COUNT().
15. For categorical rankings, use GROUP BY and ORDER BY.
16. For top results, use LIMIT.
17. For date analysis, use SQLite-compatible date functions.
18. Pay attention to the actual column data types.

ACTUAL DATASET SCHEMA:

{schema}

USER QUESTION:

{question}

Return ONLY the SQL query.
"""

    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt

        )

    except Exception as e:

        raise RuntimeError(
            f"Gemini SQL generation failed: {e}"
        )


    if response is None:

        raise RuntimeError(
            "Gemini returned no response."
        )


    sql = getattr(
        response,
        "text",
        ""
    )


    sql = clean_sql(sql)


    valid, error = validate_sql(
        sql
    )


    if not valid:

        raise ValueError(
            f"Generated SQL is invalid: {error}"
        )


    return sql


# ============================================================
# REPAIR SQL
# ============================================================

def repair_sql(
    question,
    failed_sql,
    error_message,
    df
):
    """
    Ask Gemini to repair SQL after SQLite reports
    an execution error.
    """

    if client is None:

        raise ValueError(
            "GEMINI_API_KEY is not configured."
        )

    schema = build_schema(df)

    prompt = f"""
You are an expert SQLite SQL debugging assistant.

The application generated a SQL query,
but SQLite returned an error.

USER QUESTION:
{question}

ORIGINAL SQL:
{failed_sql}

SQLITE ERROR:
{error_message}

ACTUAL DATASET SCHEMA:
{schema}

DATABASE TABLE:
sales

Your task:

1. Fix the SQL query.
2. Use ONLY columns from the schema.
3. Use ONLY the sales table.
4. Use valid SQLite syntax.
5. Preserve the original user intent.
6. Return ONLY the corrected SQL.
7. Do not use Markdown.
8. Do not explain the answer.
9. Only return a read-only SELECT/WITH query.
"""

    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt

        )

    except Exception as e:

        raise RuntimeError(
            f"Gemini SQL repair failed: {e}"
        )


    if response is None:

        raise RuntimeError(
            "Gemini returned no repair response."
        )


    sql = getattr(
        response,
        "text",
        ""
    )


    sql = clean_sql(sql)


    valid, error = validate_sql(
        sql
    )


    if not valid:

        raise ValueError(
            f"Repaired SQL is invalid: {error}"
        )


    return sql


# ============================================================
# GENERATE SQL WITH AUTOMATIC REPAIR
# ============================================================

def generate_sql_with_repair(
    question,
    df,
    connection,
    max_retries=2
):
    """
    Generate SQL, execute it and automatically
    repair the SQL if SQLite reports an error.
    """

    if not question.strip():

        raise ValueError(
            "Please enter a question."
        )


    sql = generate_sql(
        question,
        df
    )


    last_error = None


    for attempt in range(
        max_retries + 1
    ):

        try:

            result = (
                connection
                .execute(sql)
            )

            columns = [
                description[0]
                for description
                in result.description
            ]

            rows = result.fetchall()

            return sql, columns, rows


        except Exception as e:

            last_error = str(e)


            # --------------------------------------------
            # No more retries
            # --------------------------------------------

            if attempt >= max_retries:

                break


            # --------------------------------------------
            # Repair SQL
            # --------------------------------------------

            sql = repair_sql(

                question=question,

                failed_sql=sql,

                error_message=last_error,

                df=df

            )


    raise RuntimeError(
        f"SQL execution failed after "
        f"{max_retries + 1} attempt(s): "
        f"{last_error}"
    )