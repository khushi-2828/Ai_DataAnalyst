# ============================================================
# AI DATA ANALYST - DASHBOARD BUILDER
# Step 16.11.1
# ============================================================

import re
import json
import sqlite3

import pandas as pd
import numpy as np


# ============================================================
# SUPPORTED VISUALIZATION TYPES
# ============================================================

SUPPORTED_CHARTS = [
    "KPI",
    "Table",
    "Bar Chart",
    "Line Chart",
    "Pie Chart",
    "Scatter Plot",
    "Histogram",
    "Box Plot",
    "Area Chart",
]


# ============================================================
# COLUMN HELPERS
# ============================================================

def get_column_types(df):
    """
    Identify numerical, categorical and date columns.
    """

    numerical_columns = (
        df.select_dtypes(include=np.number)
        .columns
        .tolist()
    )

    categorical_columns = (
        df.select_dtypes(
            include=[
                "object",
                "category",
                "bool"
            ]
        )
        .columns
        .tolist()
    )

    date_columns = []

    for column in df.columns:

        if pd.api.types.is_datetime64_any_dtype(
            df[column]
        ):
            date_columns.append(column)

        elif df[column].dtype == "object":

            try:

                converted = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

                valid_ratio = (
                    converted.notna().mean()
                )

                if valid_ratio >= 0.8:

                    date_columns.append(
                        column
                    )

            except Exception:
                pass

    return {
        "numerical": numerical_columns,
        "categorical": categorical_columns,
        "date": date_columns,
    }


# ============================================================
# CLEAN SQL RESPONSE
# ============================================================

def clean_sql(sql):
    """
    Clean SQL returned by an AI model.
    """

    if not sql:

        return None

    sql = str(sql).strip()

    # Remove markdown code blocks
    sql = re.sub(
        r"```sql",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"```",
        "",
        sql
    )

    # Remove leading explanation
    sql_lower = sql.lower()

    select_position = sql_lower.find(
        "select"
    )

    if select_position > 0:

        sql = sql[
            select_position:
        ]

    # Remove trailing semicolon duplicates
    sql = sql.strip()

    if not sql.endswith(";"):

        sql += ";"

    return sql


# ============================================================
# VALIDATE SQL
# ============================================================

def validate_sql(sql):
    """
    Basic safety validation.

    Dashboard Builder should only execute
    read-only SELECT queries.
    """

    if not sql:

        return False, "SQL is empty."

    cleaned = sql.strip().lower()

    if not cleaned.startswith("select"):

        return (
            False,
            "Only SELECT queries are allowed."
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
    ]

    for keyword in forbidden_keywords:

        if keyword in cleaned:

            return (
                False,
                f"Unsafe SQL operation detected: {keyword.strip()}"
            )

    return True, None


# ============================================================
# EXECUTE SQL
# ============================================================

def execute_dashboard_sql(
    connection,
    sql
):
    """
    Execute a read-only SQL query
    and return a DataFrame.
    """

    valid, error = validate_sql(
        sql
    )

    if not valid:

        raise ValueError(
            error
        )

    try:

        return pd.read_sql_query(
            sql,
            connection
        )

    except Exception as e:

        raise RuntimeError(
            f"SQL execution failed: {e}"
        )


# ============================================================
# AUTOMATIC CHART SELECTION
# ============================================================

def choose_chart_type(
    question,
    result_df
):
    """
    Decide which visualization is most
    appropriate for the SQL result.
    """

    question_lower = (
        question.lower()
        if question
        else ""
    )

    if result_df is None:

        return "Table"

    if result_df.empty:

        return "Table"

    # --------------------------------------------------------
    # SINGLE VALUE → KPI
    # --------------------------------------------------------

    if (
        len(result_df) == 1
        and len(result_df.columns) == 1
    ):

        return "KPI"

    # --------------------------------------------------------
    # EXPLICIT USER WORDS
    # --------------------------------------------------------

    if "histogram" in question_lower:

        return "Histogram"

    if (
        "scatter" in question_lower
        or "relationship" in question_lower
        or "correlation" in question_lower
    ):

        return "Scatter Plot"

    if (
        "pie" in question_lower
        or "share" in question_lower
        or "percentage" in question_lower
    ):

        return "Pie Chart"

    if (
        "box plot" in question_lower
        or "boxplot" in question_lower
        or "outlier" in question_lower
    ):

        return "Box Plot"

    if "area" in question_lower:

        return "Area Chart"

    if (
        "trend" in question_lower
        or "over time" in question_lower
        or "monthly" in question_lower
        or "daily" in question_lower
        or "yearly" in question_lower
        or "weekly" in question_lower
    ):

        return "Line Chart"

    # --------------------------------------------------------
    # RESULT STRUCTURE
    # --------------------------------------------------------

    numeric_columns = (
        result_df
        .select_dtypes(
            include=np.number
        )
        .columns
        .tolist()
    )

    categorical_columns = (
        result_df
        .select_dtypes(
            include=[
                "object",
                "category",
                "bool"
            ]
        )
        .columns
        .tolist()
    )

    if (
        len(categorical_columns) >= 1
        and len(numeric_columns) >= 1
    ):

        # A small number of categories
        # works well as a bar chart.

        category_column = (
            categorical_columns[0]
        )

        unique_count = (
            result_df[
                category_column
            ]
            .nunique()
        )

        if unique_count <= 20:

            return "Bar Chart"

        return "Table"

    # --------------------------------------------------------
    # TWO NUMERICAL COLUMNS → SCATTER
    # --------------------------------------------------------

    if len(numeric_columns) >= 2:

        return "Scatter Plot"

    # --------------------------------------------------------
    # ONE NUMERICAL COLUMN
    # --------------------------------------------------------

    if len(numeric_columns) == 1:

        if len(result_df) <= 20:

            return "Bar Chart"

        return "Histogram"

    return "Table"


# ============================================================
# FIND X COLUMN
# ============================================================

def find_x_column(
    result_df,
    chart_type
):
    """
    Automatically determine the X-axis.
    """

    if result_df is None:
        return None

    columns = result_df.columns.tolist()

    if not columns:
        return None

    categorical = (
        result_df
        .select_dtypes(
            include=[
                "object",
                "category",
                "bool"
            ]
        )
        .columns
        .tolist()
    )

    date_columns = []

    for column in columns:

        try:

            converted = pd.to_datetime(
                result_df[column],
                errors="coerce"
            )

            if (
                converted.notna().mean()
                >= 0.8
            ):

                date_columns.append(
                    column
                )

        except Exception:
            pass

    # Prefer dates for line charts
    if (
        chart_type == "Line Chart"
        and date_columns
    ):

        return date_columns[0]

    # Prefer categorical columns
    if categorical:

        return categorical[0]

    return columns[0]


# ============================================================
# FIND Y COLUMN
# ============================================================

def find_y_column(
    result_df,
    x_column=None
):
    """
    Automatically determine the Y-axis.
    """

    if result_df is None:
        return None

    numeric_columns = (
        result_df
        .select_dtypes(
            include=np.number
        )
        .columns
        .tolist()
    )

    if x_column in numeric_columns:

        numeric_columns.remove(
            x_column
        )

    if numeric_columns:

        return numeric_columns[0]

    # fallback
    for column in result_df.columns:

        if column != x_column:

            return column

    return None


# ============================================================
# CREATE DASHBOARD COMPONENT
# ============================================================

def create_dashboard_component(
    question,
    sql,
    result_df,
    chart_type=None
):
    """
    Convert a question + SQL result
    into a dashboard component.
    """

    if chart_type is None:

        chart_type = choose_chart_type(
            question,
            result_df
        )

    x_column = find_x_column(
        result_df,
        chart_type
    )

    y_column = find_y_column(
        result_df,
        x_column
    )

    component = {

        "question": question,

        "sql": sql,

        "chart_type": chart_type,

        "x_column": x_column,

        "y_column": y_column,

        "rows": len(result_df)
        if result_df is not None
        else 0,

        "columns": (
            result_df.columns.tolist()
            if result_df is not None
            else []
        ),

        "data": result_df,

    }

    return component


# ============================================================
# BUILD ONE DASHBOARD COMPONENT
# ============================================================

def build_dashboard_component(
    question,
    connection,
    sql_generator
):
    """
    Complete pipeline for one question:

        Question
            ↓
        SQL Generator
            ↓
        SQL Validation
            ↓
        SQLite
            ↓
        Chart Selection
            ↓
        Dashboard Component
    """

    if not question or not question.strip():

        raise ValueError(
            "Question cannot be empty."
        )

    # --------------------------------------------------------
    # GENERATE SQL
    # --------------------------------------------------------

    sql = sql_generator(
        question
    )

    sql = clean_sql(
        sql
    )

    # --------------------------------------------------------
    # VALIDATE SQL
    # --------------------------------------------------------

    valid, error = validate_sql(
        sql
    )

    if not valid:

        raise ValueError(
            error
        )

    # --------------------------------------------------------
    # EXECUTE SQL
    # --------------------------------------------------------

    result_df = execute_dashboard_sql(
        connection,
        sql
    )

    # --------------------------------------------------------
    # CREATE COMPONENT
    # --------------------------------------------------------

    component = create_dashboard_component(
        question=question,
        sql=sql,
        result_df=result_df
    )

    return component


# ============================================================
# BUILD MULTIPLE DASHBOARD COMPONENTS
# ============================================================

def build_dashboard(
    questions,
    connection,
    sql_generator
):
    """
    Build a dashboard from multiple questions.

    Returns:

        components
        errors
    """

    components = []

    errors = []

    for index, question in enumerate(
        questions,
        start=1
    ):

        if not question:
            continue

        try:

            component = (
                build_dashboard_component(
                    question,
                    connection,
                    sql_generator
                )
            )

            component["id"] = index

            components.append(
                component
            )

        except Exception as e:

            errors.append({

                "question_number": index,

                "question": question,

                "error": str(e)

            })

    return components, errors


# ============================================================
# CHANGE CHART TYPE
# ============================================================

def update_chart_type(
    component,
    chart_type
):
    """
    Allow the user to manually change
    the visualization.
    """

    if chart_type not in SUPPORTED_CHARTS:

        raise ValueError(
            f"Unsupported chart type: {chart_type}"
        )

    component[
        "chart_type"
    ] = chart_type

    result_df = component.get(
        "data"
    )

    component[
        "x_column"
    ] = find_x_column(
        result_df,
        chart_type
    )

    component[
        "y_column"
    ] = find_y_column(
        result_df,
        component["x_column"]
    )

    return component


# ============================================================
# SERIALIZE DASHBOARD
# ============================================================

def dashboard_to_json(
    components
):
    """
    Convert dashboard configuration
    to JSON.

    Data itself is not included.
    """

    dashboard = []

    for component in components:

        dashboard.append({

            "id": component.get(
                "id"
            ),

            "question": component.get(
                "question"
            ),

            "sql": component.get(
                "sql"
            ),

            "chart_type": component.get(
                "chart_type"
            ),

            "x_column": component.get(
                "x_column"
            ),

            "y_column": component.get(
                "y_column"
            ),

            "rows": component.get(
                "rows"
            ),

            "columns": component.get(
                "columns"
            ),

        })

    return json.dumps(
        dashboard,
        indent=4,
        default=str
    )


# ============================================================
# EXPORT DASHBOARD DATA
# ============================================================

def combine_dashboard_results(
    components
):
    """
    Combine all dashboard results
    into one downloadable Excel/CSV-friendly
    structure.

    Each component gets a question column.
    """

    frames = []

    for component in components:

        data = component.get(
            "data"
        )

        if data is None:
            continue

        if data.empty:
            continue

        temp = data.copy()

        temp.insert(
            0,
            "Dashboard Question",
            component.get(
                "question",
                ""
            )
        )

        frames.append(
            temp
        )

    if not frames:

        return pd.DataFrame()

    return pd.concat(
        frames,
        ignore_index=True,
        sort=False
    )


# ============================================================
# DEFAULT DASHBOARD QUESTIONS
# ============================================================

def generate_default_questions(
    df
):
    """
    Generate useful starter questions
    based only on the dataset structure.

    These are NOT AI-generated.
    """

    questions = []

    numerical = (
        df.select_dtypes(
            include=np.number
        )
        .columns
        .tolist()
    )

    categorical = (
        df.select_dtypes(
            include=[
                "object",
                "category",
                "bool"
            ]
        )
        .columns
        .tolist()
    )

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    if numerical:

        questions.append(
            f"What is the total {numerical[0]}?"
        )

        questions.append(
            f"What is the average {numerical[0]}?"
        )

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    if categorical and numerical:

        questions.append(
            f"Show {numerical[0]} by "
            f"{categorical[0]}"
        )

    # --------------------------------------------------------
    # TOP VALUES
    # --------------------------------------------------------

    if categorical and numerical:

        questions.append(
            f"Show the top 10 "
            f"{categorical[0]} by "
            f"{numerical[0]}"
        )

    # --------------------------------------------------------
    # SECOND NUMERICAL COLUMN
    # --------------------------------------------------------

    if len(numerical) >= 2:

        questions.append(
            f"Show the relationship between "
            f"{numerical[0]} and "
            f"{numerical[1]}"
        )

    return questions[:5]