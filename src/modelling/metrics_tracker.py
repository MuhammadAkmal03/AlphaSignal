import pandas as pd
from pathlib import Path

PRED = Path("data/final/prediction/prediction_log.csv")
ACTUAL = Path("data/final/prediction/actuals_log.csv")
OUT = Path("data/final/prediction/performance_metrics.csv")

def update_metrics():
    df_pred = pd.read_csv(PRED)
    df_act = pd.read_csv(ACTUAL)

    df = pd.merge(df_pred, df_act, on="date")

    df["abs_err"] = abs(df["predicted"] - df["actual"])
    df["pct_err"] = df["abs_err"] / df["actual"] * 100

    metrics = {
        "MAE": df["abs_err"].mean(),
        "MAPE": df["pct_err"].mean()
    }

    pd.DataFrame([metrics]).to_csv(OUT, index=False)

    print("\n Updated model performance:")
    print(metrics)

if __name__ == "__main__":
    update_metrics()
