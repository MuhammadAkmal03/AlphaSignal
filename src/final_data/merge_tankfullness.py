import pandas as pd
from pathlib import Path

MASTER = Path("data/processed/master_dataset_clean.csv")
SYNTH = Path("data/raw/tank_fullness_global.csv")
OUT = Path("data/processed/master_dataset_with_fullness.csv")

def merge_fullness():
    print("\n=== Merging Tank Fullness into Master Dataset ===\n")

    df_master = pd.read_csv(MASTER)
    df_synth = pd.read_csv(SYNTH)

    # Convert to datetime
    df_master["date"] = pd.to_datetime(df_master["date"])
    df_synth["date"] = pd.to_datetime(df_synth["date"])

    # Keep only needed cols
    df_synth = df_synth[["date", "tank_fullness_global_pct"]]
    df_synth.rename(columns={
        "tank_fullness_global_pct": "tank_inventory_score"
    }, inplace=True)

    # Merge
    df = df_master.merge(df_synth, on="date", how="left", suffixes=("_old", ""))

    # If old tank_inventory_score exists → drop it
    if "tank_inventory_score_old" in df.columns:
        df.drop(columns=["tank_inventory_score_old"], inplace=True)

    # Forward fill synthetic tank fullness
    df["tank_inventory_score"] = df["tank_inventory_score"].ffill()

    # Save
    df.to_csv(OUT, index=False)

    print("\nMerged + Cleaned →", OUT)
    print(df.head())


if __name__ == "__main__":
    merge_fullness()
