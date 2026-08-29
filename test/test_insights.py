from utils.insights import generate_insights


question = "Which product sold the most?"

sql = """
SELECT
    Product,
    SUM(Quantity) AS Total_Quantity
FROM sales
GROUP BY Product
ORDER BY Total_Quantity DESC
LIMIT 1;
"""

result = """
 Product    Total_Quantity
 T-Shirt    245
"""


insights = generate_insights(
    question,
    sql,
    result
)

print("\n==============================")
print("AI BUSINESS INSIGHTS")
print("==============================")
print(insights)