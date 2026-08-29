import pandas as pd
import numpy as np


def analyze_anomalies(df):
    """
    Detect statistical anomalies in numerical columns
    using the IQR method.
    """

    results = []

    numerical_columns = (
        df
        .select_dtypes(include="number")
        .columns
        .tolist()
    )

    for column in numerical_columns:

        series = df[column].dropna()

        if len(series) < 5:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        anomalies = df[
            (df[column] < lower_bound)
            | (df[column] > upper_bound)
        ]

        for index, row in anomalies.iterrows():

            value = row[column]

            if value < lower_bound:
                distance = (
                    lower_bound - value
                )
            else:
                distance = (
                    value - upper_bound
                )

            deviation = (
                distance / abs(iqr)
                if iqr != 0
                else 0
            )

            if deviation >= 3:
                severity = "High"
            elif deviation >= 1.5:
                severity = "Medium"
            else:
                severity = "Low"

            results.append({
                "row_index": index,
                "column": column,
                "value": value,
                "lower_bound": round(
                    lower_bound, 2
                ),
                "upper_bound": round(
                    upper_bound, 2
                ),
                "deviation": round(
                    deviation, 2
                ),
                "severity": severity
            })

    return results


def create_anomaly_dataframe(
    anomaly_results
):

    if not anomaly_results:
        return pd.DataFrame()

    return pd.DataFrame(
        anomaly_results
    )