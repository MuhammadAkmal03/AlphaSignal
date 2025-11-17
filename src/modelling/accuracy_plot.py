import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PRED = Path("data/final/prediction/prediction_log.csv")
ACTUAL = Path("data/final/prediction/actuals_log.csv")
OUT = Path("data/final/prediction/accuracy_plot.png")


def generate_plot():
    print("\n Generating accuracy plot...")

    # Check prediction log exists
    if not PRED.exists():
        print(" No predictions found → cannot generate plot.")
        return

    # Check actuals exist
    if not ACTUAL.exists():
        print(" No actuals available yet → skipping accuracy plot for today.")
        return

    df_pred = pd.read_csv(PRED)
    df_act = pd.read_csv(ACTUAL)

    df_pred["date"] = pd.to_datetime(df_pred["date"])
    df_act["date"] = pd.to_datetime(df_act["date"])

    # Match previous day's prediction to the actual price
    df_pred["match_date"] = df_pred["date"] - pd.Timedelta(days=1)

    merged = df_pred.merge(
        df_act, left_on="match_date", right_on="date", suffixes=("_pred", "_act")
    )

    if merged.empty:
        print(" No matching data for plotting yet.")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(merged["match_date"], merged["actual"], label="Actual Price")
    plt.plot(merged["match_date"], merged["predicted"], label="Predicted Price")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title("Prediction vs Actual")
    plt.legend()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT)
    plt.close()

    print(f" Plot saved → {OUT}")


if __name__ == "__main__":
    generate_plot()
