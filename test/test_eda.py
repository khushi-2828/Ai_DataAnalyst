import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.data_loader import load_data
from utils.data_cleaner import clean_data
from utils.eda import generate_eda_report


DATA_PATH = PROJECT_ROOT / "data" / "sales_data.csv"


# Load data
df = load_data(DATA_PATH)

# Clean data
df, duplicates_removed = clean_data(df)

# Generate EDA report
report = generate_eda_report(df)


print("\n========== EDA REPORT ==========")

print("\nRows:")
print(report["rows"])

print("\nColumns:")
print(report["columns"])

print("\nNumerical Columns:")
print(report["numerical_columns"])

print("\nCategorical Columns:")
print(report["categorical_columns"])

print("\nStatistics:")
print(report["statistics"])

print("\nTop Categories:")
print(report["top_categories"])

print("\nCorrelation:")
print(report["correlation"])