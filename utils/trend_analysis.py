import pandas as pd


def analyze_sales_trend(df):

    result = {}

    # Find date column
    date_column = None

    possible_date_columns = [
        "order_date",
        "date",
        "sales_date",
        "transaction_date"
    ]

    for column in possible_date_columns:
        if column in df.columns:
            date_column = column
            break

    # Find sales column
    sales_column = None

    possible_sales_columns = [
        "sales",
        "revenue",
        "amount",
        "total_sales",
        "total_amount"
    ]

    for column in possible_sales_columns:
        if column in df.columns:
            sales_column = column
            break

    if not date_column or not sales_column:
        return {
            "error": "Date or sales column not found"
        }

    # Make a copy
    data = df.copy()

    # Convert date
    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )

    # Remove invalid dates
    data = data.dropna(
        subset=[date_column]
    )

    # Create month
    data["month"] = data[date_column].dt.to_period("M")

    # Monthly sales
    monthly_sales = (
        data.groupby("month")[sales_column]
        .sum()
        .sort_index()
    )

    # Month-over-month growth
    monthly_growth = monthly_sales.pct_change() * 100

    result["monthly_sales"] = {
        str(month): round(value, 2)
        for month, value in monthly_sales.items()
    }

    result["monthly_growth"] = {
        str(month): round(value, 2)
        for month, value in monthly_growth.dropna().items()
    }

    # Best month
    if not monthly_sales.empty:
        best_month = monthly_sales.idxmax()

        result["best_month"] = str(best_month)
        result["best_month_sales"] = round(
            monthly_sales.max(), 2
        )

    # Lowest month
    if not monthly_sales.empty:
        worst_month = monthly_sales.idxmin()

        result["lowest_month"] = str(worst_month)
        result["lowest_month_sales"] = round(
            monthly_sales.min(), 2
        )

    return result