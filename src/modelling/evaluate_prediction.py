import os
import pandas as pd
from pathlib import Path

PRED_FILE = Path("data/final/prediction/latest_prediction.txt")
PRED_LOG = Path("data/final/prediction/predictions_log.csv")
ACTUAL_LOG = Path("data/final/prediction/actuals_log.csv")
METRICS_OUT = Path("data/final/prediction/performance_metrics.csv")


# 1. Load last prediction
def load_latest_prediction():
    if not PRED_FILE.exists():
        raise FileNotFoundError(f"Missing → {PRED_FILE}")

    with open(PRED_FILE, "r") as f:
        lines = f.read().strip().split("\n")

    predicted_date = lines[0].split(":")[1].strip()
    predicted_value = float(lines[1].split(":")[1].strip())

    return predicted_date, predicted_value


# 2. Load last actual close price
def load_latest_actual():
    if not ACTUAL_LOG.exists():
        raise FileNotFoundError(f"Missing actual file → {ACTUAL_LOG}")

    df = pd.read_csv(ACTUAL_LOG)
    df["date"] = pd.to_datetime(df["date"])

    last_row = df.iloc[-1]
    return last_row["date"].strftime("%Y-%m-%d"), float(last_row["actual"])


# 3. Update predictions log
def update_predictions_log(date, pred):
    PRED_LOG.parent.mkdir(parents=True, exist_ok=True)

    if PRED_LOG.exists():
        df = pd.read_csv(PRED_LOG)
    else:
        df = pd.DataFrame(columns=["date", "predicted"])

    df.loc[len(df)] = [date, pred]
    df.to_csv(PRED_LOG, index=False)


# 4. Compute accuracy only if dates match
def compute_metrics():
    if not PRED_LOG.exists() or not ACTUAL_LOG.exists():
        print("Not enough data for evaluation yet.")
        return

    predictions = pd.read_csv(PRED_LOG)
    actuals = pd.read_csv(ACTUAL_LOG)

    predictions["date"] = pd.to_datetime(predictions["date"])
    actuals["date"] = pd.to_datetime(actuals["date"])

    merged = predictions.merge(actuals, on="date", how="inner")

    if merged.empty:
        print("\n⚠ No matching actual/prediction dates yet.")
        print("Wait for tomorrow. Evaluation cannot run today.\n")
        return

    merged["error"] = abs(merged["predicted"] - merged["actual"])
    merged["ape"] = abs((merged["predicted"] - merged["actual"]) / merged["actual"]) * 100

    mae = merged["error"].mean()
    mape = merged["ape"].mean()

    METRICS_OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"MAE": [mae], "MAPE": [mape]}).to_csv(METRICS_OUT, index=False)

    print("\n Updated Model Performance:")
    print(f"MAE  = {mae:.4f}")
    print(f"MAPE = {mape:.2f}%")
    print(f"Metrics saved → {METRICS_OUT}\n")


# MAIN EXECUTION
def evaluate():
    print("\n=== Evaluating Model Prediction vs Actual ===\n")

    pred_date, pred_value = load_latest_prediction()
    act_date, act_value = load_latest_actual()

    print(f"Predicted:  {pred_date} = {pred_value}")
    print(f"Actual:     {act_date} = {act_value}")

    # Store prediction
    update_predictions_log(pred_date, pred_value)

    # Evaluate if possible
    compute_metrics()


if __name__ == "__main__":
    evaluate()
