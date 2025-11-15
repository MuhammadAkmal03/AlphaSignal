import pandas as pd
from pathlib import Path

def convert_nlp_to_daily():
    PROCESSED = Path("data/processed")
    infile = PROCESSED / "demand_score.csv"
    outfile = PROCESSED / "demand_score_daily.csv"

    df = pd.read_csv(infile)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Create full daily range
    start = df["date"].min()
    end = df["date"].max()
    daily_index = pd.date_range(start, end, freq="D")

    df_daily = pd.DataFrame({"date": daily_index})

    # Merge and forward-fill
    df_daily = df_daily.merge(df, on="date", how="left")
    df_daily["demand_score"] = df_daily["demand_score"].ffill().bfill()

    df_daily.to_csv(outfile, index=False)

    print("\n Created DAILY NLP scores!")
    print("Saved:", outfile)


if __name__ == "__main__":
    convert_nlp_to_daily()
