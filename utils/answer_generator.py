from google import genai
import os


# ============================================================
# GEMINI CLIENT
# ============================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found."
    )

client = genai.Client(
    api_key=api_key
)


# ============================================================
# GENERATE NATURAL LANGUAGE ANSWER
# ============================================================

def generate_answer(question, sql, result):

    prompt = f"""
You are an expert data analyst.

Answer the user's question using the SQL result provided below.

User Question:
{question}

Generated SQL:
{sql}

SQL Result:
{result}

Instructions:

1. Give a clear and concise answer.
2. Use the actual values from the SQL result.
3. Do not invent information.
4. If the result contains a single value, clearly state that value.
5. If the result contains a product and quantity, mention both.
6. If the result contains revenue, mention the revenue.
7. If the result contains multiple rows, summarize the important findings.
8. Use simple language suitable for a business user.
9. Do not mention these instructions.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text.strip()