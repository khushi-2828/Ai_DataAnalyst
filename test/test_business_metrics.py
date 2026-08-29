import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.data_loader import load_data
from utils.data_cleaner import clean_data
from utils.business_metrics import calculate_business_metrics


DATA_PATH = PROJECT_ROOT / "data" / "sales_data.csv"


# Load data
df = load_data(DATA_PATH)

# Clean data
df, duplicates_removed = clean_data(df)

# Calculate business metrics
metrics = calculate_business_metrics(df)


print("\n========== BUSINESS METRICS ==========")

for metric, value in metrics.items():
    print(f"{metric}: {value}")