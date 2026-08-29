import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.data_loader import load_data
from utils.data_cleaner import clean_data
from utils.sql_engine import create_database, run_query


DATA_PATH = PROJECT_ROOT / "data" / "sales_data.csv"
DATABASE_PATH = PROJECT_ROOT / "data" / "analytics.db"


# Load data
df = load_data(DATA_PATH)

# Clean data
df, duplicates_removed = clean_data(df)

# Create SQLite database
connection = create_database(
    df,
    DATABASE_PATH
)


# Business analysis using SQL
query = """
SELECT
    Product,
    SUM(Quantity) AS units_sold,
    SUM(Quantity * Price) AS total_sales
FROM sales
GROUP BY Product
ORDER BY total_sales DESC
LIMIT 10;
"""

query = """
SELECT
    Category,
    SUM(Quantity) AS units_sold,
    SUM(Quantity * Price) AS total_sales
FROM sales
GROUP BY Category
ORDER BY total_sales DESC;
"""
query = """
SELECT
    City,
    SUM(Quantity * Price) AS total_sales
FROM sales
GROUP BY City
ORDER BY total_sales DESC
LIMIT 10;
"""

result = run_query(
    connection,
    query
)


print("\n========== SQL BUSINESS ANALYSIS ==========")
print(result)


connection.close()