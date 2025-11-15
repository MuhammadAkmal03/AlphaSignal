import yfinance as yf
from pathlib import Path

def fetch_uso_data():
    RAW = Path("data/raw")
    RAW.mkdir(parents=True, exist_ok=True)

    df = yf.download("USO", period="5y", auto_adjust=False)

    df = df.reset_index()   # brings "Date" out of index
    df = df[["Date", "Close"]]
    df.columns = ["date", "close_price"]

    df.to_csv(RAW / "uso_price.csv", index=False)
    print("USO price saved:", RAW / "uso_price.csv")

if __name__ == "__main__":
    fetch_uso_data()
