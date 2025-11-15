import pandas as pd
from pathlib import Path

# ---------------- PATHS ----------------
MASTER_CLEAN = Path("data/processed/master_dataset_clean.csv")
SYNTHETIC = Path("data/raw/tank_fullness_global.csv")
YOLO = Path("data/processed/tank_fullness_yolo.csv")
OUTPUT = Path("data/final/master_cleaned.csv")

# ----------------------------------------
def load_and_prepare():
    df_master = pd.read_csv(MASTER_CLEAN)
    df_master["date"] = pd.to_datetime(df_master["date"])

    df_synth = pd.read_csv(SYNTHETIC)
    df_synth["date"] = pd.to_datetime(df_synth["date"])
    df_synth = df_synth[["date", "tank_fullness_global_pct"]].rename(
        columns={"tank_fullness_global_pct": "synthetic_score"}
    )

    df_yolo = pd.read_csv(YOLO)
    df_yolo["date"] = pd.to_datetime(df_yolo["date"])
    df_yolo = df_yolo[["date", "tank_fullness_global_pct"]].rename(
        columns={"tank_fullness_global_pct": "yolo_score"}
    )

    return df_master, df_synth, df_yolo


def merge_fullness():
    print("\n===== CLEAN MERGE PIPELINE START =====\n")

    df_master, df_synth, df_yolo = load_and_prepare()

    # 1) Merge synthetic
    df = df_master.merge(df_synth, on="date", how="left")

    # 2) Merge YOLO
    df = df.merge(df_yolo, on="date", how="left")

    # 3) Create the FINAL SCORE (your model must use this)
    df["tank_inventory_score"] = df["yolo_score"].fillna(df["synthetic_score"])

    # 4) Fill small gaps (YOLO missing days → synthetic missing days)
    df = df.sort_values("date")
    df["tank_inventory_score"] = df["tank_inventory_score"].ffill().bfill()

    # 5) Drop helper columns
    df = df.drop(columns=["synthetic_score", "yolo_score"])

    # 6) Save
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)

    print("\n===== MERGE COMPLETE =====")
    print(f"Saved → {OUTPUT}")
    print(df.head())


if __name__ == "__main__":
    merge_fullness()
