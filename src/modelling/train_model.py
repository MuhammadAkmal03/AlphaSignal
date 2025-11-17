import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
import joblib

DATA = Path("data/final/train/train_dataset.csv")
MODEL_OUT = Path("models/xgb_model.pkl")
SCALER_OUT = Path("models/scaler.pkl")
METRICS_OUT = Path("data/final/train/model_metrics.txt")

def train_model():
    df = pd.read_csv(DATA)

    # Split X and y
    X = df.drop(columns=["close_price"])
    y = df["close_price"]

    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    # Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # XGBoost Model
    model = XGBRegressor(
        n_estimators=600,
        learning_rate=0.04,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    model.fit(X_train_scaled, y_train)

    # Evaluation
    preds = model.predict(X_test_scaled)

    mae = mean_absolute_error(y_test, preds)
    mse = mean_squared_error(y_test, preds)
    rmse = mse ** 0.5                         
    mape = np.mean(np.abs((y_test - preds) / y_test)) * 100

    # Save model + scaler
    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_OUT)
    joblib.dump(scaler, SCALER_OUT)

    print("\n MODEL TRAINED SUCCESSFULLY!")
    print(f"Model saved → {MODEL_OUT}")
    print(f"Scaler saved → {SCALER_OUT}")
    print(" Evaluation:")
    print(f"   MAE  = {mae:.3f}")
    print(f"   RMSE = {rmse:.3f}")
    print(f"   MAPE = {mape:.3f}%")

if __name__ == "__main__":
    train_model()
