"""
Enhanced NLP Daily Converter
Converts quarterly demand scores to daily, then replaces forward-filled values 
with real-time news sentiment when available
"""
import pandas as pd
from pathlib import Path

def convert_nlp_to_daily():
    PROCESSED = Path("data/processed")
    RAW = Path("data/raw")
    
    infile = PROCESSED / "demand_score.csv"
    outfile = PROCESSED / "demand_score_daily.csv"
    news_sentiment_file = RAW / "nlp" / "realtime_news_sentiment.csv"

    # Load quarterly demand scores
    df = pd.read_csv(infile)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Create full daily range
    start = df["date"].min()
    end = df["date"].max()
    
    # Extend to today if real-time news is available
    if news_sentiment_file.exists():
        news_df = pd.read_csv(news_sentiment_file)
        news_df["date"] = pd.to_datetime(news_df["date"])
        news_end = news_df["date"].max()
        if news_end > end:
            end = news_end
            print(f"✅ Extending date range to {end} using real-time news")

    daily_index = pd.date_range(start, end, freq="D")
    df_daily = pd.DataFrame({"date": daily_index})

    # Merge quarterly scores and forward-fill
    df_daily = df_daily.merge(df, on="date", how="left")
    
    # Mark which values are forward-filled (for replacement)
    df_daily["is_original"] = df_daily["demand_score"].notna()
    df_daily["demand_score"] = df_daily["demand_score"].ffill().bfill()

    # Replace forward-filled values with real-time news sentiment
    if news_sentiment_file.exists():
        print("✅ Loading real-time news sentiment to replace forward-filled values...")
        news_df = pd.read_csv(news_sentiment_file)
        news_df["date"] = pd.to_datetime(news_df["date"])
        
        # Merge news sentiment
        df_daily = df_daily.merge(
            news_df[["date", "news_sentiment"]], 
            on="date", 
            how="left"
        )
        
        # Replace forward-filled demand_score with news_sentiment where available
        # Only replace if it was forward-filled (not original data)
        mask = (~df_daily["is_original"]) & (df_daily["news_sentiment"].notna())
        replaced_count = mask.sum()
        
        df_daily.loc[mask, "demand_score"] = df_daily.loc[mask, "news_sentiment"]
        
        print(f"✅ Replaced {replaced_count} forward-filled values with real-time news sentiment")
        
        # Drop helper columns
        df_daily = df_daily.drop(columns=["is_original", "news_sentiment"])
    else:
        print("⚠️  No real-time news sentiment found - using forward-fill only")
        df_daily = df_daily.drop(columns=["is_original"])

    # Save
    df_daily.to_csv(outfile, index=False)

    print(f"\n✅ Created DAILY NLP scores!")
    print(f"   Saved: {outfile}")
    print(f"   Date range: {df_daily['date'].min()} to {df_daily['date'].max()}")
    print(f"   Total days: {len(df_daily)}")


if __name__ == "__main__":
    convert_nlp_to_daily()
