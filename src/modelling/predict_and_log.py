import sys, os
import pandas as pd
from pathlib import Path
import joblib
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

from src.features.utils_feature import (
    add_lag_features,
    add_rolling_features,
    add_date_features,
    add_interaction,
)

MASTER = Path("data/final/master_dataset_cleaned.csv")
SELECTED = Path("data/final/features/selected_features.csv")

MODEL = Path("models/xgb_model.pkl")
SCALER = Path("models/scaler.pkl")

LOG = Path("data/final/prediction/prediction_log.csv")
LATEST = Path("data/final/prediction/latest_prediction.txt")


def recreate_features(df):
    df = df.copy()

    df = add_lag_features(df, "close_price")
    df = add_rolling_features(df, "close_price")

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


def predict_and_log():
    df = pd.read_csv(MASTER)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")

    latest = recreate_features(df).iloc[-1:]
    selected = pd.read_csv(SELECTED)["feature"].tolist()
    latest = latest[selected].ffill().bfill()

    model = joblib.load(MODEL)
    scaler = joblib.load(SCALER)

    pred = model.predict(scaler.transform(latest))[0]
    today = datetime.utcnow().date()

    LOG.parent.mkdir(parents=True, exist_ok=True)
    row = pd.DataFrame([{"date": today, "predicted": pred}])

    if LOG.exists():
        pd.concat([pd.read_csv(LOG), row]).to_csv(LOG, index=False)
    else:
        row.to_csv(LOG, index=False)

    with open(LATEST, "w") as f:
        f.write(str(pred))

    print(f"\n Prediction logged → {LOG}")
    print(f"Predicted next-day close: {pred:.2f}")


if __name__ == "__main__":
    predict_and_log()
