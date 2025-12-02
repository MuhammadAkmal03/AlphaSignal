"""
Extract real feature names from training dataset
"""
import pandas as pd
import json
from pathlib import Path

TRAIN_DATA = Path("data/final/train/train_dataset.csv")
OUTPUT_PATH = Path("models/feature_names.json")

try:
    # Read just the first row to get column names
    df = pd.read_csv(TRAIN_DATA, nrows=1)
    
    # Get all columns except the target variable
    # Assuming 'close' or 'target' or 'price' is the target
    all_columns = df.columns.tolist()
    
    # Remove common target column names
    target_names = ['close', 'target', 'price', 'label', 'y', 'Close']
    feature_names = [col for col in all_columns if col not in target_names]
    
    print(f"✓ Found {len(feature_names)} features in training data")
    print(f"✓ Total columns: {len(all_columns)}")
    print(f"\nFirst 15 features:")
    for i, name in enumerate(feature_names[:15], 1):
        print(f"  {i}. {name}")
    
    # Save to JSON
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(feature_names, f, indent=2)
    
    print(f"\n✓ Saved {len(feature_names)} feature names to {OUTPUT_PATH}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
