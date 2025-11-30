"""
Generate Historical Predictions for Backtesting
Creates predictions for past dates using the trained model
"""
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from datetime import datetime, timedelta
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.features.utils_feature import (
    add_lag_features,
    add_rolling_features,
    add_date_features,
    add_interaction,
)

# Paths
MASTER = Path("data/final/master_dataset_cleaned.csv")
SELECTED = Path("data/final/features/selected_features.csv")
MODEL = Path("models/xgb_model.pkl")
SCALER = Path("models/scaler.pkl")
PREDICTION_LOG = Path("data/final/prediction/prediction_log.csv")


def recreate_features(df):
    """Recreate features for prediction"""
    df = df.copy()

    df = add_lag_features(df, "close_price")
    df = add_rolling_features(df, "close_price")

    ports = [
        "Houston","Singapore","Rotterdam","Fujairah","RasTanura",
        "Antwerp","Qingdao","Dalian","CorpusChristi","PortArthur",
        "Fawley_UK","MinaAlAhmadi","Yokohama","Ulsan","Mumbai"
    ]

    for p in ports:
        df = add_lag_features(df, p, lags=[1,7,14])
        df = add_rolling_features(df, p)

    df = add_interaction(df, "tank_inventory_score", "wti_price")
    df = add_interaction(df, "Singapore", "diesel_price")
    df = add_interaction(df, "demand_score", "close_price")

    df = add_date_features(df)

    return df


def generate_historical_predictions(lookback_days=180):
    """
    Generate predictions for historical dates
    
    Args:
        lookback_days: Number of days to generate predictions for
    """
    print("=" * 60)
    print("Generating Historical Predictions for Backtesting")
    print("=" * 60)
    
    # Load data
    print(f"\n Loading master dataset...")
    df = pd.read_csv(MASTER)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    
    # Load model and scaler
    print(" Loading model and scaler...")
    model = joblib.load(MODEL)
    scaler = joblib.load(SCALER)
    selected = pd.read_csv(SELECTED)["feature"].tolist()
    
    # Get date range
    end_date = df.index.max()
    start_date = end_date - timedelta(days=lookback_days)
    
    print(f"\n Generating predictions from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Generate predictions for each date
    predictions = []
    
    for current_date in pd.date_range(start_date, end_date, freq='D'):
        # Get data up to current date
        df_up_to_date = df[df.index <= current_date].copy()
        
        if len(df_up_to_date) < 30:  # Need enough data for features
            continue
        
        # Recreate features
        df_features = recreate_features(df_up_to_date)
        
        # Get latest row
        latest = df_features.iloc[-1:]
        
        # Select features
        try:
            latest_features = latest[selected].ffill().bfill()
        except KeyError:
            continue  # Skip if features don't exist
        
        # Make prediction
        try:
            pred = model.predict(scaler.transform(latest_features))[0]
            
            predictions.append({
                'date': current_date,
                'predicted': pred
            })
            
            if len(predictions) % 30 == 0:
                print(f"   Generated {len(predictions)} predictions...")
                
        except Exception as e:
            continue
    
    # Save predictions
    if predictions:
        pred_df = pd.DataFrame(predictions)
        
        # Load existing predictions if any
        if PREDICTION_LOG.exists():
            existing = pd.read_csv(PREDICTION_LOG)
            existing['date'] = pd.to_datetime(existing['date'])
            
            # Combine and remove duplicates
            combined = pd.concat([existing, pred_df])
            combined = combined.drop_duplicates(subset=['date'], keep='last')
            combined = combined.sort_values('date')
        else:
            combined = pred_df
        
        # Save
        PREDICTION_LOG.parent.mkdir(parents=True, exist_ok=True)
        combined.to_csv(PREDICTION_LOG, index=False)
        
        print(f"\n Generated {len(predictions)} predictions")
        print(f" Saved to: {PREDICTION_LOG}")
        print(f"\n Prediction Summary:")
        print(f"   Date Range: {pred_df['date'].min().strftime('%Y-%m-%d')} to {pred_df['date'].max().strftime('%Y-%m-%d')}")
        print(f"   Avg Prediction: ${pred_df['predicted'].mean():.2f}")
        print(f"   Min Prediction: ${pred_df['predicted'].min():.2f}")
        print(f"   Max Prediction: ${pred_df['predicted'].max():.2f}")
        
        print("\n" + "=" * 60)
        print(" Historical Predictions Generated!")
        print("=" * 60)
        print("\nYou can now run backtesting:")
        print("  python src/backtesting/run_backtest.py")
        
    else:
        print("\n No predictions generated. Check if model and data are available.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate historical predictions for backtesting')
    parser.add_argument('--days', type=int, default=180,
                       help='Number of days to generate predictions for (default: 180)')
    
    args = parser.parse_args()
    
    generate_historical_predictions(lookback_days=args.days)
