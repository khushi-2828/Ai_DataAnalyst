import pandas as pd


def profile_dataset(df):

    profile = {}

    profile["rows"] = len(df)

    profile["columns"] = len(df.columns)

    profile["missing_values"] = int(
        df.isnull().sum().sum()
    )

    profile["duplicate_rows"] = int(
        df.duplicated().sum()
    )

    profile["numerical_columns"] = (
        df.select_dtypes(
            include="number"
        ).columns.tolist()
    )

    profile["categorical_columns"] = (
        df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()
    )

    profile["date_columns"] = []

    for column in df.columns:

        converted = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        if converted.notna().mean() > 0.8:

            profile["date_columns"].append(
                column
            )

    return profile