import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

ACTUALS = Path("data/final/prediction/actuals_log.csv")

def fetch_price(date):
    df = yf.download("BZ=F", start=date, end=date + timedelta(days=1), progress=False)
    if df.empty:
        return None
    return float(df["Close"].iloc[0])

def update_actuals():
    today = datetime.utcnow().date()
    target_date = today - timedelta(days=1)

    price = fetch_price(target_date)
    if price is None:
        print("No market data is available yet.")
        return

    row = pd.DataFrame([{"date": target_date, "actual": price}])

    if ACTUALS.exists():
        pd.concat([pd.read_csv(ACTUALS), row]).to_csv(ACTUALS, index=False)
    else:
        row.to_csv(ACTUALS, index=False)

    print(f"Actual logged → {ACTUALS}")

if __name__ == "__main__":
    update_actuals()
