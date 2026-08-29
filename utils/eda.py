def prepare_eda_for_ai(eda_results):
    """
    Convert EDA results into a compact text format
    that can be sent to the AI model.
    """

    if not eda_results:
        return "No EDA results are available."

    output = []

    output.append(
        f"Rows: {eda_results.get('rows', 0)}"
    )

    output.append(
        f"Columns: {eda_results.get('columns', 0)}"
    )

    output.append(
        f"Duplicate Rows: "
        f"{eda_results.get('duplicate_rows', 0)}"
    )

    # --------------------------------------------------------
    # NUMERICAL INFORMATION
    # --------------------------------------------------------

    numerical = eda_results.get(
        "numerical",
        {}
    )

    if numerical:

        output.append(
            "\nNUMERICAL ANALYSIS:"
        )

        for column, values in numerical.items():

            output.append(
                f"\n{column}:"
            )

            if isinstance(values, dict):

                for key, value in values.items():

                    output.append(
                        f"  {key}: {value}"
                    )

    # --------------------------------------------------------
    # CATEGORICAL INFORMATION
    # --------------------------------------------------------

    categorical = eda_results.get(
        "categorical",
        {}
    )

    if categorical:

        output.append(
            "\nCATEGORICAL ANALYSIS:"
        )

        for column, values in categorical.items():

            output.append(
                f"\n{column}:"
            )

            if isinstance(values, dict):

                for key, value in values.items():

                    output.append(
                        f"  {key}: {value}"
                    )

    # --------------------------------------------------------
    # CORRELATION
    # --------------------------------------------------------

    correlation = eda_results.get(
        "correlation"
    )

    if correlation is not None:

        output.append(
            "\nCORRELATION MATRIX:"
        )

        try:

            output.append(
                correlation.to_string()
            )

        except Exception:

            output.append(
                str(correlation)
            )

    # --------------------------------------------------------
    # DATE COLUMNS
    # --------------------------------------------------------

    date_columns = eda_results.get(
        "date_columns",
        []
    )

    if date_columns:

        output.append(
            "\nDATE COLUMNS:"
        )

        output.append(
            ", ".join(date_columns)
        )

    # --------------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------------

    missing_values = eda_results.get(
        "missing_values",
        {}
    )

    if missing_values:

        output.append(
            "\nMISSING VALUES:"
        )

        for column, count in (
            missing_values.items()
        ):

            if count > 0:

                output.append(
                    f"{column}: {count}"
                )

    return "\n".join(output)