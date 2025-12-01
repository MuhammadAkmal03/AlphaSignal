import pandas as pd
from pathlib import Path
import json
import math

PREDICTION_LOG = Path("data/final/prediction/prediction_log.csv")

try:
    print(f"Reading {PREDICTION_LOG}...")
    df = pd.read_csv(PREDICTION_LOG)
    
    print("Converting dates...")
    df['date'] = pd.to_datetime(df['date'])
    
    print("Sorting...")
    df = df.sort_values('date', ascending=False)
    
    days = 30
    df = df.head(days)
    
    print("Checking for NaNs...")
    if df['predicted'].isnull().any():
        print("WARNING: Found NaNs in 'predicted' column!")
        print(df[df['predicted'].isnull()])
    
    print("Simulating response construction...")
    predictions = []
    for i, (_, row) in enumerate(df.iterrows()):
        try:
            p_val = float(row['predicted'])
            if math.isnan(p_val):
                print(f"Row {i} has NaN predicted price")
            
            pred = {
                "date": row['date'].strftime('%Y-%m-%d'),
                "predicted_price": p_val,
                "timestamp": row['date'].isoformat()
            }
            predictions.append(pred)
        except Exception as e:
            print(f"Error constructing row {i}: {e}")
            raise e
            
    print("Simulating JSON serialization...")
    try:
        json_output = json.dumps(predictions)
        print("JSON serialization successful")
    except Exception as e:
        print(f"JSON serialization FAILED: {e}")
        # Check for NaN specifically
        for p in predictions:
            if math.isnan(p['predicted_price']):
                print("Found NaN in predictions list, which fails JSON serialization")
                break

except Exception as e:
    print(f"FAILED: {e}")
