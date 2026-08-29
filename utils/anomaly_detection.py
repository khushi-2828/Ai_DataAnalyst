import pandas as pd


def detect_anomalies(df):

    anomalies = []

    if df is None or df.empty:
        return anomalies

    # Find numerical columns
    numeric_columns = (
        df
        .select_dtypes(include="number")
        .columns
        .tolist()
    )

    if not numeric_columns:
        return anomalies

    for column in numeric_columns:

        # Need enough observations
        if len(df[column].dropna()) < 4:
            continue

        values = df[column].dropna()

        # Calculate quartiles
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)

        iqr = q3 - q1

        # Avoid zero IQR
        if iqr == 0:
            continue

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Find anomalies
        anomaly_rows = df[
            (df[column] < lower_bound) |
            (df[column] > upper_bound)
        ]

        for index, row in anomaly_rows.iterrows():

            anomalies.append({
                "column": column,
                "row": index,
                "value": row[column],
                "type": (
                    "High"
                    if row[column] > upper_bound
                    else "Low"
                )
            })

    return anomalies