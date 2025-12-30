"""
Generate Historical Predictions
Creates 6 months of historical Brent oil predictions for analytics display

This script fetches actual Brent oil prices and generates realistic
predicted prices with small variations, simulating model predictions.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import yfinance as yf

OUTPUT_DIR = Path("data/final/prediction")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch_brent_prices(months=6):
    """
    Fetch historical Brent crude oil prices using yfinance
    
    Args:
        months: Number of months of historical data
    
    Returns:
        pd.DataFrame: DataFrame with date and close price
    """
    print(f" Fetching {months} months of Brent crude prices...")
    
    # Brent Crude Oil Futures
    ticker = "BZ=F"
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if data.empty:
            print(" No data from yfinance, using synthetic data")
            return generate_synthetic_prices(months)
        
        df = data[['Close']].reset_index()
        df.columns = ['date', 'actual_price']
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        print(f" Retrieved {len(df)} days of price data")
        print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"   Price range: ${df['actual_price'].min():.2f} - ${df['actual_price'].max():.2f}")
        
        return df
    
    except Exception as e:
        print(f" Error fetching data: {e}")
        return generate_synthetic_prices(months)

def generate_synthetic_prices(months=6):
    """Generate synthetic Brent prices if API fails"""
    print(" Generating synthetic Brent prices...")
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=months * 30)
    
    dates = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days
    
    # Start around $75 and add random walk
    base_price = 75.0
    prices = [base_price]
    
    for _ in range(len(dates) - 1):
        change = np.random.normal(0, 1.5)  # Daily change ~$1.50 std
        new_price = prices[-1] + change
        new_price = max(60, min(95, new_price))  # Keep in realistic range
        prices.append(new_price)
    
    df = pd.DataFrame({
        'date': dates.date,
        'actual_price': prices
    })
    
    return df

def add_prediction_variation(df, variation_pct=2.0):
    """
    Add small variation to actual prices to simulate model predictions
    
    Args:
        df: DataFrame with actual_price column
        variation_pct: Maximum percentage variation (default 2%)
    
    Returns:
        pd.DataFrame: DataFrame with predicted prices
    """
    print(f" Generating predictions with ±{variation_pct}% variation...")
    
    # Add random variation to simulate predictions
    np.random.seed(42)  # For reproducibility
    
    variation = np.random.uniform(-variation_pct/100, variation_pct/100, len(df))
    df['predicted'] = df['actual_price'] * (1 + variation)
    df['predicted'] = df['predicted'].round(2)
    
    # Calculate error metrics
    mae = np.mean(np.abs(df['actual_price'] - df['predicted']))
    mape = np.mean(np.abs((df['actual_price'] - df['predicted']) / df['actual_price'])) * 100
    
    print(f" Generated {len(df)} predictions")
    print(f"   MAE: ${mae:.2f}")
    print(f"   MAPE: {mape:.2f}%")
    
    return df

def save_prediction_log(df):
    """Save predictions in the format expected by the API"""
    
    # Format for prediction_log.csv
    output = df[['date', 'predicted']].copy()
    output['date'] = pd.to_datetime(output['date'])
    
    output_path = OUTPUT_DIR / "prediction_log.csv"
    output.to_csv(output_path, index=False)
    
    print(f"\n Saved prediction log: {output_path}")
    print(f"   Total predictions: {len(output)}")
    
    # Also save latest prediction
    latest = output.iloc[-1]['predicted']
    latest_path = OUTPUT_DIR / "latest_prediction.txt"
    with open(latest_path, 'w') as f:
        f.write(str(latest))
    
    print(f" Saved latest prediction: ${latest:.2f}")
    
    return output_path

def main():
    print("\n" + "="*60)
    print(" HISTORICAL PREDICTIONS GENERATOR")
    print("="*60)
    
    # Fetch actual prices
    df = fetch_brent_prices(months=6)
    
    # Generate predictions with variation
    df = add_prediction_variation(df, variation_pct=1.5)
    
    # Save to prediction log
    output_path = save_prediction_log(df)
    
    print("\n" + "="*60)
    print(" COMPLETE!")
    print(f"   Output: {output_path}")
    print("="*60)
    
    return df

if __name__ == "__main__":
    main()
