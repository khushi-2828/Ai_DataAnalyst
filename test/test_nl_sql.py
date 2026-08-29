from utils.nl_to_sql import generate_sql
from utils.data_loader import load_data
from utils.sql_engine import run_query
from utils.answer_generator import generate_answer

import sqlite3


# ============================================================
# 1. LOAD DATA
# ============================================================

df = load_data("data/sales_data.csv")


# ============================================================
# 2. CREATE SQLITE DATABASE
# ============================================================

connection = sqlite3.connect(":memory:")


# ============================================================
# 3. CREATE SALES TABLE
# ============================================================

df.to_sql(
    "sales",
    connection,
    index=False,
    if_exists="replace"
)


# ============================================================
# 4. ASK USER QUESTION
# ============================================================

question = input("\nQuestion: ")


print("\n" + "=" * 60)
print("Question:", question)


# ============================================================
# 5. GENERATE SQL USING GEMINI
# ============================================================

try:

    sql = generate_sql(question)

    print("\nGenerated SQL:")
    print(sql)


except Exception as e:

    print("\nGemini SQL Generation Error:")
    print(e)

    connection.close()
    exit()


# ============================================================
# 6. EXECUTE SQL
# ============================================================

try:

    result = run_query(
        connection,
        sql
    )

    print("\nSQL Result:")
    print(result)


except Exception as e:

    print("\nSQL Execution Error:")
    print(e)

    connection.close()
    exit()


# ============================================================
# 7. GENERATE NATURAL LANGUAGE ANSWER
# ============================================================

try:

    answer = generate_answer(
        question,
        sql,
        result.to_string(index=False)
    )

    print("\n" + "=" * 60)
    print("FINAL ANSWER:")
    print(answer)


except Exception as e:

    print("\nAnswer Generation Error:")
    print(e)


# ============================================================
# 8. CLOSE DATABASE
# ============================================================

connection.close()