import os
from google import genai


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found.")


client = genai.Client(
    api_key=api_key
)


def explain_anomalies(question, result, anomalies):

    if not anomalies:
        return "No significant anomalies were detected."


    anomaly_text = "\n".join(
        [
            f"- Column: {a['column']}, "
            f"Row: {a['row']}, "
            f"Value: {a['value']}, "
            f"Type: {a['type']}"
            for a in anomalies
        ]
    )


    prompt = f"""
You are an expert business data analyst.

The user asked:

{question}

The SQL analysis produced this result:

{result}

The following anomalies were detected:

{anomaly_text}

Explain the anomalies in simple business language.

Requirements:

1. Clearly identify each unusual value.
2. Explain whether it is unusually high or low.
3. Explain why it may matter to the business.
4. Do not invent causes.
5. If the cause cannot be determined from the data, say that.
6. Mention the actual numerical values.
7. Keep the explanation concise.
8. Use bullet points.
9. Do not mention SQL, Python, Gemini, or programming.

Return only the anomaly explanation.
"""


    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )


    return response.text.strip()