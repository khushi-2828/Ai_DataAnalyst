import pandas as pd


def clean_data(df):

    df = df.copy()

    # 1. Remove completely empty rows
    df = df.dropna(how="all")

    # 2. Remove duplicate rows
    duplicates_removed = df.duplicated().sum()
    df = df.drop_duplicates()

    # 3. Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # 4. Try to convert date columns
    for column in df.columns:
        if "date" in column:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    # 5. Handle missing numerical values
    numerical_columns = df.select_dtypes(
        include="number"
    ).columns

    for column in numerical_columns:
        df[column] = df[column].fillna(
            df[column].median()
        )

    # 6. Handle missing categorical values
    categorical_columns = df.select_dtypes(
        include="object"
    ).columns

    for column in categorical_columns:
        df[column] = df[column].fillna("Unknown")

    return df, duplicates_removed