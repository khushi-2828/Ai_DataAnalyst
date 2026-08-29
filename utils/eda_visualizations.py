import pandas as pd
import matplotlib.pyplot as plt


def numerical_histogram(df, column, bins=20):

    fig, ax = plt.subplots()

    ax.hist(
        df[column].dropna(),
        bins=bins
    )

    ax.set_title(
        f"Distribution of {column}"
    )

    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")

    return fig


def numerical_boxplot(df, column):

    fig, ax = plt.subplots()

    ax.boxplot(
        df[column].dropna()
    )

    ax.set_title(
        f"Box Plot of {column}"
    )

    ax.set_ylabel(column)

    return fig


def categorical_bar_chart(
    df,
    column,
    top_n=10
):

    counts = (
        df[column]
        .value_counts()
        .head(top_n)
    )

    fig, ax = plt.subplots()

    counts.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        f"Top {top_n} Values - {column}"
    )

    ax.set_xlabel(column)
    ax.set_ylabel("Count")

    plt.xticks(
        rotation=45,
        ha="right"
    )

    return fig


def date_trend_chart(
    df,
    date_column,
    value_column
):

    temp = df[
        [
            date_column,
            value_column
        ]
    ].copy()

    temp[date_column] = pd.to_datetime(
        temp[date_column],
        errors="coerce"
    )

    temp = temp.dropna(
        subset=[
            date_column,
            value_column
        ]
    )

    trend = (
        temp
        .groupby(date_column)[value_column]
        .sum()
        .sort_index()
    )

    fig, ax = plt.subplots()

    trend.plot(
        ax=ax
    )

    ax.set_title(
        f"{value_column} Trend"
    )

    ax.set_xlabel(
        date_column
    )

    ax.set_ylabel(
        value_column
    )

    plt.xticks(
        rotation=45,
        ha="right"
    )

    return fig


def correlation_heatmap(
    df,
    numerical_columns
):

    if len(numerical_columns) < 2:

        return None

    correlation = (
        df[numerical_columns]
        .corr()
    )

    fig, ax = plt.subplots()

    image = ax.imshow(
        correlation,
        aspect="auto"
    )

    ax.set_xticks(
        range(
            len(correlation.columns)
        )
    )

    ax.set_yticks(
        range(
            len(correlation.columns)
        )
    )

    ax.set_xticklabels(
        correlation.columns,
        rotation=45,
        ha="right"
    )

    ax.set_yticklabels(
        correlation.columns
    )

    ax.set_title(
        "Correlation Heatmap"
    )

    fig.colorbar(
        image,
        ax=ax
    )

    return fig