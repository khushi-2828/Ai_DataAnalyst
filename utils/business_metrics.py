import pandas as pd


def calculate_business_metrics(df):

    metrics = {}

    # -------------------------
    # Revenue / Sales
    # -------------------------
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

    if sales_column:
        metrics["total_sales"] = round(
            df[sales_column].sum(), 2
        )

        metrics["average_sales"] = round(
            df[sales_column].mean(), 2
        )

        metrics["maximum_sale"] = round(
            df[sales_column].max(), 2
        )

        metrics["minimum_sale"] = round(
            df[sales_column].min(), 2
        )

    # -------------------------
    # Orders
    # -------------------------
    order_column = None

    possible_order_columns = [
        "order_id",
        "orderid",
        "order"
    ]

    for column in possible_order_columns:
        if column in df.columns:
            order_column = column
            break

    if order_column:
        metrics["total_orders"] = df[order_column].nunique()

    # -------------------------
    # Customers
    # -------------------------
    customer_column = None

    possible_customer_columns = [
        "customer_id",
        "customerid",
        "customer"
    ]

    for column in possible_customer_columns:
        if column in df.columns:
            customer_column = column
            break

    if customer_column:
        metrics["total_customers"] = df[customer_column].nunique()

    # -------------------------
    # Quantity
    # -------------------------
    if "quantity" in df.columns:
        metrics["total_quantity"] = int(
            df["quantity"].sum()
        )

        metrics["average_quantity"] = round(
            df["quantity"].mean(), 2
        )

    return metrics