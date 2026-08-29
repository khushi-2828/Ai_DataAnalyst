import pandas as pd


def load_data(file_path):
    df = pd.read_csv(file_path)

    print("Dataset loaded successfully!")
    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])

    return df