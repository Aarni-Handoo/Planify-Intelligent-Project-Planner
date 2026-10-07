import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

RAW_FILE = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "tasks.csv"
)

PROCESSED_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)

PROCESSED_FILE = os.path.join(
    PROCESSED_DIR,
    "tasks_processed.csv"
)


def preprocess_dataset():

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    df = pd.read_csv(RAW_FILE)

    priority_mapping = {
        "Low": 1,
        "Medium": 2,
        "High": 3
    }

    role_mapping = {
        "frontend": 0,
        "backend": 1,
        "database": 2,
        "design": 3,
        "devops": 4
    }

    df["priority_value"] = df["priority"].map(
        priority_mapping
    )

    df["role_value"] = df["role"].map(
        role_mapping
    )

    df["skill_count"] = df["skills"].apply(
        lambda x: len(x.split(","))
    )

    df["description_length"] = df["description"].apply(
        lambda x: len(str(x).split())
    )

    df.to_csv(
        PROCESSED_FILE,
        index=False
    )

    print("Dataset preprocessing completed.")
    print("Output:", PROCESSED_FILE)
    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())


if __name__ == "__main__":
    preprocess_dataset()