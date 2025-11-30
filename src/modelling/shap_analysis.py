"""
SHAP Analysis - Simplified Version
Works directly with unscaled data to avoid numpy compatibility issues
"""
import pandas as pd
import numpy as np
import shap
import joblib
from pathlib import Path
import matplotlib.pyplot as plt

DATA_PATH = Path("data/final/train/train_dataset.csv")
MODEL_PKL = Path("models/xgb_model.pkl")
OUTPUT_PATH = Path("models/shap_summary.png")

print("=" * 60)
print("SHAP Feature Importance Analysis")
print("=" * 60)

print("\n Loading model & data...")

# Load model
if not MODEL_PKL.exists():
    raise FileNotFoundError(f" Model not found: {MODEL_PKL}")

model = joblib.load(MODEL_PKL)
print(" Model loaded successfully")

# Load data
df = pd.read_csv(DATA_PATH)
X = df.drop(columns=["close_price"])
y = df["close_price"]

# Use a sample for faster computation
sample_size = min(500, len(X))
X_sample = X.sample(n=sample_size, random_state=42)

print(f" Loaded {len(df)} training samples")
print(f" Using {sample_size} samples for SHAP analysis")
print(f" Features: {X_sample.shape[1]}")

# Create SHAP explainer
print("\n Creating SHAP explainer...")
explainer = shap.TreeExplainer(model)

# Calculate SHAP values
print(" Calculating SHAP values (may take 1-2 minutes)...")
shap_values = explainer.shap_values(X_sample)

print(" SHAP values calculated successfully")

# Generate summary plot
print("\n Generating SHAP summary plot...")
plt.figure(figsize=(14, 10))
shap.summary_plot(shap_values, X_sample, show=False, max_display=20)
plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches='tight')
print(f" Plot saved: {OUTPUT_PATH}")

# Generate feature importance bar plot
print(" Generating feature importance bar plot...")
OUTPUT_BAR = Path("models/shap_importance_bar.png")
plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False, max_display=20)
plt.tight_layout()
plt.savefig(OUTPUT_BAR, dpi=150, bbox_inches='tight')
print(f" Bar plot saved: {OUTPUT_BAR}")

# Calculate mean absolute SHAP values for feature ranking
print("\n Top 10 Most Important Features:")
print("-" * 60)
feature_importance = pd.DataFrame({
    'feature': X_sample.columns,
    'importance': np.abs(shap_values).mean(axis=0)
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.head(10).iterrows():
    print(f"  {row['feature']:30s} {row['importance']:.4f}")

# Display plots
plt.show()

print("\n" + "=" * 60)
print(" SHAP Analysis Complete!")
print("=" * 60)
print(f" Summary plot: {OUTPUT_PATH}")
print(f" Bar plot: {OUTPUT_BAR}")
print(f" Analyzed {sample_size} samples")
