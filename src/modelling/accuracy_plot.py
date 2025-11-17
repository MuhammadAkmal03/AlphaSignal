import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PRED = Path("data/final/prediction/prediction_log.csv")
ACTUAL = Path("data/final/prediction/actuals_log.csv")
OUT = Path("data/final/prediction/accuracy_plot.png")

def generate_plot():
    df_pred = pd.read_csv(PRED)
    df_act = pd.read_csv(ACTUAL)

    df = pd.merge(df_pred, df_act, on="date")
    df["date"] = pd.to_datetime(df["date"])

    plt.figure(figsize=(12,6))
    plt.plot(df["date"], df["predicted"], label="Predicted Price")
    plt.plot(df["date"], df["actual"], label="Actual Price")
    plt.xlabel("Date")
    plt.ylabel("Brent Close Price (USD)")
    plt.title("Prediction vs Actual Brent Price")
    plt.legend()
    plt.grid(True)
    plt.savefig(OUT)

    print(f"Plot saved → {OUT}")

if __name__ == "__main__":
    generate_plot()
