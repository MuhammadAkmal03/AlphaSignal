import yfinance as yf
from pathlib import Path

def fetch_uso_data():
    df = yf.download("USO", period="5y", auto_adjust=False)
    df = df[["Close"]].rename(columns={"Close": "close_price"}).reset_index()

    RAW = Path("data/raw")
    RAW.mkdir(parents=True, exist_ok=True)

    df.to_csv(RAW / "uso_price.csv", index=False)

    print(" USO price saved at:", RAW / "uso_price.csv")

# run
if __name__ == "__main__":
    fetch_uso_data()

