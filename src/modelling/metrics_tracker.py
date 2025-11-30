import pandas as pd
from pathlib import Path

PRED = Path("data/final/prediction/prediction_log.csv")
ACTUAL = Path("data/final/prediction/actuals_log.csv")
OUT = Path("data/final/prediction/performance_metrics.csv")


def update_metrics():
    print("\n📊 Updating performance metrics...")

    # --- Check prediction exists ---
    if not PRED.exists():
        print("   No prediction log found. Skipping metrics update.")
        return

    # --- Check actual file exists ---
    if not ACTUAL.exists():
        print("   ⚠️  No actuals file yet. Metrics will be calculated once actual prices are available.")
        print("   ✅ Prediction saved successfully!")
        return

    # Load both
    df_pred = pd.read_csv(PRED)
    df_act = pd.read_csv(ACTUAL)

    # Align dates (actual is always 1 day behind prediction)
    # Use coerce to handle any parsing errors gracefully
    df_pred["date"] = pd.to_datetime(df_pred["date"], errors='coerce').dt.normalize()
    df_act["date"] = pd.to_datetime(df_act["date"], errors='coerce').dt.normalize()
    
    # Drop any rows where date parsing failed
    df_pred = df_pred.dropna(subset=["date"])
    df_act = df_act.dropna(subset=["date"])

    df_pred["match_date"] = df_pred["date"] - pd.Timedelta(days=1)

    merged = df_pred.merge(
        df_act, left_on="match_date", right_on="date", suffixes=("_pred", "_act")
    )

    if merged.empty:
        print(" No matching actual for yesterday's prediction yet.")
        return

    # Compute metrics
    merged["AE"] = (merged["predicted"] - merged["actual"]).abs()
    merged["APE"] = (merged["AE"] / merged["actual"]) * 100

    mae = merged["AE"].mean()
    mape = merged["APE"].mean()

    # Save
    df_out = pd.DataFrame({"MAE": [mae], "MAPE": [mape]})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(OUT, index=False)

    print(" Metrics updated →", OUT)
    print(df_out)


if __name__ == "__main__":
    update_metrics()
