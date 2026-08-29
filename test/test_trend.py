import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.data_loader import load_data
from utils.data_cleaner import clean_data
from utils.trend_analysis import analyze_sales_trend


DATA_PATH = PROJECT_ROOT / "data" / "sales_data.csv"


# Load data
df = load_data(DATA_PATH)

# Clean data
df, duplicates_removed = clean_data(df)

# Analyze trends
trend = analyze_sales_trend(df)


print("\n========== TREND ANALYSIS ==========")

if "error" in trend:

    print(trend["error"])

else:

    print("\nMonthly Sales:")

    for month, sales in trend["monthly_sales"].items():
        print(f"{month}: {sales}")

    print("\nMonthly Growth:")

    for month, growth in trend["monthly_growth"].items():
        print(f"{month}: {growth}%")

    print("\nBest Month:")
    print(trend.get("best_month"))

    print("\nBest Month Sales:")
    print(trend.get("best_month_sales"))

    print("\nLowest Month:")
    print(trend.get("lowest_month"))

    print("\nLowest Month Sales:")
    print(trend.get("lowest_month_sales"))