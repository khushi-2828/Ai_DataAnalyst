import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.data_loader import load_data
from utils.data_profiler import profile_data


DATA_PATH = PROJECT_ROOT / "data" / "sales_data.csv"

df = load_data(DATA_PATH)

profile = profile_data(df)

print("\n========== DATA PROFILE ==========")

print("\nRows:")
print(profile["rows"])

print("\nColumns:")
print(profile["columns"])

print("\nColumn Names:")
print(profile["column_names"])

print("\nData Types:")
print(profile["data_types"])

print("\nMissing Values:")
print(profile["missing_values"])

print("\nDuplicate Rows:")
print(profile["duplicate_rows"])

print("\nNumerical Columns:")
print(profile["numerical_columns"])

print("\nCategorical Columns:")
print(profile["categorical_columns"])