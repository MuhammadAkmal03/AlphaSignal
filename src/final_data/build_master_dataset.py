import os
import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
PROCESSED = Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)

# Load CSV (EIA + USO + AIS + NLP)

def load_csv(path, value_col_name):
    """
    Loads CSV and renames the date column correctly.

    - USO has 'date'
    - EIA has 'period'
    - AIS/NLP already have 'date'
    """
    df = pd.read_csv(path)

    # Detect date column
    if "date" in df.columns:
        date_col = "date"
    elif "period" in df.columns:
        date_col = "period"
    else:
        raise ValueError(f"No date or period column found in: {path}")

    # Standardize -> `date`
    df.rename(columns={date_col: "date"}, inplace=True)

    # To datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Rename `value` column for EIA
    if "value" in df.columns:
        df.rename(columns={"value": value_col_name}, inplace=True)

    # Only keep needed columns
    if value_col_name in df.columns:
        return df[["date", value_col_name]]

    raise ValueError(f"Column '{value_col_name}' not found in {path}")

#  Build Master Dataset
def build_master():
    print("\n=== Rebuilding Clean Master Dataset ===\n")

    # Load AIS counts (daily)
    ais = pd.read_csv(RAW / "ships" / "s_ship_counts.csv")
    ais["date"] = pd.to_datetime(ais["date"])

    # Load NLP demand score
    nlp = pd.read_csv(PROCESSED / "demand_score.csv")
    nlp["date"] = pd.to_datetime(nlp["date"])

    # Load USO price
    uso = load_csv(RAW / "uso_price.csv", "close_price")

    # Load EIA products
    wti = load_csv(RAW / "eia" / "WTI_Crude.csv", "wti_price")
    gas = load_csv(RAW / "eia" / "NY_Gasoline.csv", "gasoline_price")
    diesel = load_csv(RAW / "eia" / "NY_Diesel.csv", "diesel_price")

    # Merge all
    df = ais.copy()

    df = df.merge(nlp, on="date", how="left")
    df = df.merge(uso, on="date", how="left")
    df = df.merge(wti, on="date", how="left")
    df = df.merge(gas, on="date", how="left")
    df = df.merge(diesel, on="date", how="left")

    # Tank Inventory Score (dummy for now)
    df["tank_inventory_score"] = 0

    # Sort
    df = df.sort_values("date")

    # Save
    out_path = PROCESSED / "master_dataset.csv"
    df.to_csv(out_path, index=False)

    print("Master dataset saved →", out_path)
    print("Rows:", len(df))


if __name__ == "__main__":
    build_master()
