import pandas as pd
from pathlib import Path
from utils_feature import *
import warnings
warnings.filterwarnings("ignore")

DATA_PATH = Path("data/final/master_dataset_cleaned.csv")
SAVE_PATH = Path("data/final/features/engineered_features.csv")

def engineer_features():
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()

    target = "close_price"

    # 1. Lag + Rolling for target
    df = add_lag_features(df, target)          
    df = add_rolling_features(df, target)      

    # AIS ports
    ais_ports = [
        "Houston","Singapore","Rotterdam","Fujairah","RasTanura",
        "Antwerp","Qingdao","Dalian","CorpusChristi","PortArthur",
        "Fawley_UK","MinaAlAhmadi","Yokohama","Ulsan","Mumbai"
    ]

    for port in ais_ports:
        if port in df.columns:                       
            df = add_lag_features(df, port, lags=[1,7])
            df = add_rolling_features(df, port)

    # 2. Interactions
    df = add_interaction(df, "tank_inventory_score", "wti_price")
    df = add_interaction(df, "Singapore", "diesel_price")
    df = add_interaction(df, "demand_score", "close_price")

    # 3. Date features
    df = add_date_features(df)

    df = df.fillna(method="ffill").fillna(method="bfill")

    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAVE_PATH)

    print("\n Feature engineering completed!")
    print(f"Engineered file saved → {SAVE_PATH}")
    print(f"Total rows: {df.shape[0]}")
    print(f"Total columns: {df.shape[1]}")

if __name__ == "__main__":
    engineer_features()
