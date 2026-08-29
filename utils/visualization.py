import pandas as pd


def recommend_visualization(df):

    if df is None or df.empty:
        return "No Chart"

    if len(df.columns) < 2:
        return "No Chart"

    numeric_columns = (
        df.select_dtypes(
            include="number"
        ).columns.tolist()
    )

    if len(numeric_columns) == 0:
        return "No Chart"

    first_column = df.columns[0]

    # Date/time result → Line Chart
    if (
        pd.api.types.is_datetime64_any_dtype(
            df[first_column]
        )
    ):
        return "Line Chart"

    # Detect month/year/day text columns
    if isinstance(
        first_column,
        str
    ):

        column_name = first_column.lower()

        if any(
            word in column_name
            for word in [
                "date",
                "day",
                "month",
                "year",
                "time"
            ]
        ):
            return "Line Chart"

    # Two or more numerical columns
    if len(numeric_columns) >= 2:

        return "Scatter Plot"

    # Small number of categories
    if len(df) <= 10:

        return "Pie Chart"

    # Default
    return "Bar Chart"