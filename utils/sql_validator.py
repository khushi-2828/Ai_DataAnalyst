import re


def validate_sql(sql):

    if not sql:
        raise ValueError("Empty SQL query generated.")

    sql = sql.strip()

    # Only allow SELECT queries
    if not re.match(r"^\s*SELECT\b", sql, re.IGNORECASE):
        raise ValueError(
            "Only SELECT queries are allowed."
        )

    # Block dangerous SQL commands
    forbidden_keywords = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "CREATE",
        "ATTACH",
        "DETACH",
        "PRAGMA"
    ]

    for keyword in forbidden_keywords:

        pattern = rf"\b{keyword}\b"

        if re.search(
            pattern,
            sql,
            re.IGNORECASE
        ):

            raise ValueError(
                f"Unsafe SQL detected: {keyword}"
            )

    return sql