import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.data_loader import load_data
from utils.data_cleaner import clean_data


DATA_PATH = PROJECT_ROOT / "data" / "sales_data.csv"

# Load original data
df = load_data(DATA_PATH)

print("\n========== BEFORE CLEANING ==========")

print("Shape:", df.shape)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())


# Clean data
cleaned_df, duplicates_removed = clean_data(df)

print("\n========== AFTER CLEANING ==========")

print("Shape:", cleaned_df.shape)

print("\nMissing values:")
print(cleaned_df.isnull().sum())

print("\nDuplicate rows:")
print(cleaned_df.duplicated().sum())

print("\nColumns:")
print(cleaned_df.columns.tolist())

print("\nData types:")
print(cleaned_df.dtypes)

print("\nDuplicates removed:", duplicates_removed)