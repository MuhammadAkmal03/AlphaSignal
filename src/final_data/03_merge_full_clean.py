import pandas as pd
from pathlib import Path

MASTER = Path("data/processed/master_dataset_clean.csv")
YOLO = Path("data/processed/tank_fullness_yolo.csv")
PAST = Path("data/raw/tank_fullness_past.csv")
OUT = Path("data/final/master_dataset_cleaned.csv")

def load_master():
    df = pd.read_csv(MASTER)
    df["date"] = pd.to_datetime(df["date"])
    return df

def load_past():
    df = pd.read_csv(PAST)
    df["date"] = pd.to_datetime(df["date"])
    df.rename(columns={"past_inventory": "past_fullness"}, inplace=True)
    return df

def load_yolo():
    if not YOLO.exists():
        print(" YOLO missing — fallback to past only.")
        return pd.DataFrame(columns=["date", "yolo_fullness"])

    df = pd.read_csv(YOLO)
    df["date"] = pd.to_datetime(df["date"])

    # detect fullness column
    for col in ["fullness_pct", "fullness", "tank_fullness_global_pct"]:
        if col in df.columns:
            fullness_col = col
            break
    else:
        raise KeyError(f"YOLO file missing fullness column. Found: {df.columns}")

    df = df.groupby("date")[fullness_col].mean().reset_index()
    df.rename(columns={fullness_col: "yolo_fullness"}, inplace=True)
    return df

def merge_fullness():
    print("\n===== CLEAN MERGE PIPELINE START =====\n")

    df_master = load_master()
    df_past = load_past()
    df_yolo = load_yolo()

    df = df_master.merge(df_past, on="date", how="left")
    df = df.merge(df_yolo, on="date", how="left")

    # FINAL INVENTORY SCORE
    df["tank_inventory_score"] = (
        df["yolo_fullness"].fillna(df["past_fullness"])
    )

    df["tank_inventory_score"] = df["tank_inventory_score"].ffill().bfill()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    print("Master cleaned & merged", OUT)
    print("Rows:", len(df))
    print("\n===== CLEAN MERGE PIPELINE END =====\n")

if __name__ == "__main__":
    merge_fullness()
