import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import joblib

DATA_PATH = Path("data/final/features/engineered_features.csv")
SAVE_SELECTED = Path("data/final/features/selected_features.csv")
SAVE_RF = Path("data/final/features/feature_importance_rf.csv")
SAVE_XGB = Path("data/final/features/feature_importance_xgb.csv")
MODEL_SAVE = Path("models/feature_selector.pkl")

def feature_selection():
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()

    y = df["close_price"]
    X = df.drop(columns=["close_price"])

    # 1. Correlation Filter (remove collinear)
    corr = X.corr()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop = [
        col for col in upper.columns
        if any(abs(upper[col]) > 0.92)
    ]
    X = X.drop(columns=to_drop)

    # 2. RandomForest Feature Importance
    rf = RandomForestRegressor(n_estimators=400, random_state=42)
    rf.fit(X, y)

    rf_imp = pd.DataFrame({
        "feature": X.columns,
        "importance": rf.feature_importances_
    }).sort_values("importance", ascending=False)

    rf_imp.to_csv(SAVE_RF, index=False)

    # 3. XGBoost Feature Importance
    xgb = XGBRegressor(
        n_estimators=600,
        learning_rate=0.04,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    xgb.fit(X, y)

    xgb_imp = pd.DataFrame({
        "feature": X.columns,
        "importance": xgb.feature_importances_
    }).sort_values("importance", ascending=False)

    xgb_imp.to_csv(SAVE_XGB, index=False)

    # 4. Select top features
    top_rf = rf_imp.head(25)["feature"]
    top_xgb = xgb_imp.head(25)["feature"]

    final_features = list(set(top_rf) | set(top_xgb))

    pd.DataFrame({"feature": final_features}).to_csv(SAVE_SELECTED, index=False)

    joblib.dump(final_features, MODEL_SAVE)

    print("\n Feature Selection Completed!")
    print(f"Selected Features Saved → {SAVE_SELECTED}")
    print(f"RandomForest Importance → {SAVE_RF}")
    print(f"XGBoost Importance → {SAVE_XGB}")
    print(f"Total selected features: {len(final_features)}")

if __name__ == "__main__":
    feature_selection()
