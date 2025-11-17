import os
import sys
import pandas as pd
from pathlib import Path
import joblib
import yfinance as yf
from datetime import timedelta

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.features.utils_feature import (
    add_lag_features,
    add_rolling_features,
    add_date_features,
    add_interaction,
)

MASTER_DATA = Path("data/final/master_dataset_cleaned.csv")
SELECTED_FEATURES = Path("data/final/features/selected_features.csv")
MODEL_PATH = Path("models/xgb_model.pkl")
SCALER_PATH = Path("models/scaler.pkl")
OUT = Path("data/final/prediction/backtest_last_30days.csv")

WINDOW = 150  


def recreate_features(df):
    df = df.copy()
    target = "close_price"

    # Target
    df = add_lag_features(df, target)
    df = add_rolling_features(df, target)

    ports = [
        "Houston","Singapore","Rotterdam","Fujairah","RasTanura",
        "Antwerp","Qingdao","Dalian","CorpusChristi","PortArthur",
        "Fawley_UK","MinaAlAhmadi","Yokohama","Ulsan","Mumbai"
    ]

    for p in ports:
        df = add_lag_features(df, p, lags=[1,7,14])
        df = add_rolling_features(df, p)

    df = add_interaction(df, "tank_inventory_score", "wti_price")
    df = add_interaction(df, "Singapore", "diesel_price")
    df = add_interaction(df, "demand_score", "close_price")

    df = add_date_features(df)

    return df


def get_real_price(date):
    try:
        df = yf.download("BZ=F", start=date, end=date + timedelta(days=1), progress=False)
        if df.empty:
            return None
        return float(df["Close"].iloc[0])
    except:
        return None


def backtest_last_30_days():
    print("\n Running Backtest for Last 30 Days...\n")

    # LOAD MASTER
    df = pd.read_csv(MASTER_DATA)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()


    df_last = df.tail(WINDOW)

    # recreate features
    df_feat = recreate_features(df_last)
    df_feat = df_feat.dropna()

    # SAFETY CHECK
    if df_feat.empty:
        print(" ERROR: Not enough historical data to compute lag/rolling features.\n"
              "Increase WINDOW to 200–300 days.")
        return

    # Load selected features
    selected = pd.read_csv(SELECTED_FEATURES)["feature"].tolist()
    df_feat = df_feat[selected]

    # MODEL + SCALER
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    df_scaled = scaler.transform(df_feat)
    preds = model.predict(df_scaled)

    # Build results
    result = pd.DataFrame({
        "date": df_feat.index + pd.Timedelta(days=1),
        "predicted": preds
    })

    # REAL PRICES
    actuals = [get_real_price(d.date()) for d in result["date"]]
    result["actual"] = actuals

    result["error"] = result["actual"] - result["predicted"]
    result["abs_error"] = result["error"].abs()
    result["pct_error"] = (result["abs_error"] / result["actual"]) * 100

    OUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUT, index=False)

    print(" Backtest saved →", OUT)
    print(result.tail())
    print("\n Backtest Completed!\n")


if __name__ == "__main__":
    backtest_last_30_days()
