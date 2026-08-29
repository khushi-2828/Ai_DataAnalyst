import os
from google import genai


# ============================================================
# GEMINI CLIENT
# ============================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found."
    )

client = genai.Client(
    api_key=api_key
)


# ============================================================
# GENERATE BUSINESS INSIGHTS
# ============================================================

def generate_insights(
    question,
    sql,
    result
):

    prompt = f"""
You are an expert business data analyst.

Analyze the SQL result and provide useful business insights.

USER QUESTION:
{question}

SQL QUERY:
{sql}

SQL RESULT:
{result}

Your task:

1. Identify the most important finding.
2. Mention important numerical values.
3. Identify the highest and lowest values when meaningful.
4. Mention trends when the result contains dates or months.
5. Mention the top-performing product, category, or city when applicable.
6. Do not invent information that is not present in the result.
7. Keep the response concise and easy to understand.
8. Use bullet points.
9. Use simple business language.
10. Do not mention SQL, Python, Gemini, or programming.

Return only the business insights.
"""


    # ========================================================
    # GEMINI REQUEST
    # ========================================================

    response = client.models.generate_content(

        model="gemini-3.5-flash-lite",

        contents=prompt
    )


    # ========================================================
    # CLEAN RESPONSE
    # ========================================================

    insights = response.text.strip()

    return insights