import pandas as pd
import shap
import xgboost as xgb
import joblib
from pathlib import Path

DATA_PATH = Path("data/final/train/train_dataset.csv")
MODEL_JSON = Path("models/xgb_model.json")
SCALER_PATH = Path("models/scaler.pkl")

print(" Loading model & data...")

# ===== LOAD BOOSTER MODEL DIRECTLY =====
if not MODEL_JSON.exists():
    raise FileNotFoundError(f" XGBoost JSON model missing → {MODEL_JSON}")

booster = xgb.Booster()
booster.load_model(str(MODEL_JSON))

print(" Booster model loaded")

# ===== LOAD DATA =====
df = pd.read_csv(DATA_PATH)
X = df.drop(columns=["close_price"])

# ===== LOAD SCALER =====
scaler = joblib.load(SCALER_PATH)
X_scaled = scaler.transform(X)

print(" Creating SHAP explainer...")


explainer = shap.TreeExplainer(booster)

shap_values = explainer(X_scaled)

print(" Generating SHAP summary plot...")
shap.summary_plot(shap_values.values, X, show=True)
