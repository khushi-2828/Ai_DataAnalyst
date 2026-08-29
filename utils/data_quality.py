import pandas as pd


def check_data_quality(df):

    quality = {}


    # ============================================================
    # MISSING VALUES
    # ============================================================

    missing = df.isnull().sum()

    missing = missing[
        missing > 0
    ]

    quality["missing_values"] = (
        missing.to_dict()
    )


    # ============================================================
    # DUPLICATE ROWS
    # ============================================================

    quality["duplicate_rows"] = int(
        df.duplicated().sum()
    )


    # ============================================================
    # DUPLICATE ORDER IDs
    # ============================================================

    quality["duplicate_order_ids"] = 0

    if "Order_ID" in df.columns:

        quality["duplicate_order_ids"] = int(
            df["Order_ID"].duplicated().sum()
        )


    # ============================================================
    # NEGATIVE NUMBERS
    # ============================================================

    negative_values = {}

    numerical_columns = (
        df.select_dtypes(
            include="number"
        ).columns
    )


    for column in numerical_columns:

        count = int(
            (df[column] < 0).sum()
        )

        if count > 0:

            negative_values[column] = count


    quality["negative_values"] = (
        negative_values
    )


    # ============================================================
    # ZERO VALUES
    # ============================================================

    zero_values = {}

    for column in numerical_columns:

        count = int(
            (df[column] == 0).sum()
        )

        if count > 0:

            zero_values[column] = count


    quality["zero_values"] = (
        zero_values
    )


    # ============================================================
    # CONSTANT COLUMNS
    # ============================================================

    constant_columns = []

    for column in df.columns:

        if df[column].nunique(
            dropna=False
        ) <= 1:

            constant_columns.append(
                column
            )


    quality["constant_columns"] = (
        constant_columns
    )


    # ============================================================
    # INVALID DATES
    # ============================================================

    invalid_dates = {}

    for column in df.columns:

        # Only check columns whose names
        # suggest they contain dates.

        if (
            "date" in column.lower()
            or "time" in column.lower()
        ):

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            invalid_count = int(
                converted.isna().sum()
            )

            if invalid_count > 0:

                invalid_dates[column] = (
                    invalid_count
                )


    quality["invalid_dates"] = (
        invalid_dates
    )


    # ============================================================
    # RETURN RESULT
    # ============================================================

    return quality