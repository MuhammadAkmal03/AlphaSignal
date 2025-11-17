import pandas as pd
import numpy as np
from pathlib import Path

MASTER_DATES = Path("data/processed/master_dataset.csv")
OUT_PAST = Path("data/raw/tank_fullness_past.csv")

def generate_past_inventory():
    print("\n=== Generating Past Tank Inventory Score ===\n")

    df = pd.read_csv(MASTER_DATES)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    np.random.seed(42)
    base = np.linspace(35, 75, len(df))
    noise = np.random.normal(0, 2.5, len(df))

    df["past_inventory"] = base + noise
    df["past_inventory"] = df["past_inventory"].clip(20, 95)

    OUT_PAST.parent.mkdir(parents=True, exist_ok=True)
    df[["date", "past_inventory"]].to_csv(OUT_PAST, index=False)

    print(" Past inventory saved →", OUT_PAST)
    print("Rows:", len(df))

if __name__ == "__main__":
    generate_past_inventory()
