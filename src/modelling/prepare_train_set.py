import pandas as pd
from pathlib import Path

FEATURES_PATH = Path("data/final/features/engineered_features.csv")
SELECTED_PATH = Path("data/final/features/selected_features.csv")
TRAIN_OUT = Path("data/final/train/train_dataset.csv")

def prepare_train_set():
    df = pd.read_csv(FEATURES_PATH)
    df["date"] = pd.to_datetime(df["date"])

    selected = pd.read_csv(SELECTED_PATH)["feature"].tolist()

    # Ensure target is there
    target = "close_price"
    selected.append(target)

    df_train = df[selected].dropna()

    TRAIN_OUT.parent.mkdir(parents=True, exist_ok=True)
    df_train.to_csv(TRAIN_OUT, index=False)

    print("\n Training dataset created!")
    print(f"Saved to → {TRAIN_OUT}")
    print(f"Rows: {len(df_train)}, Columns: {df_train.shape[1]}")

if __name__ == "__main__":
    prepare_train_set()
