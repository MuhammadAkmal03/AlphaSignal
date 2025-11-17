import pandas as pd
import numpy as np

# --- Small safe lag windows ---
def add_lag_features(df, col, lags=[1, 7]):
    for lag in lags:
        df[f"{col}_lag_{lag}"] = df[col].shift(lag)
    return df


# --- Only small rolling windows ---
def add_rolling_features(df, col):
    df[f"{col}_7ma"] = df[col].rolling(7, min_periods=1).mean()
    df[f"{col}_7vol"] = df[col].rolling(7, min_periods=1).std()
    return df


# --- Date features ---
def add_date_features(df):
    df = df.copy()
    df["year"] = df.index.year
    df["month"] = df.index.month
    df["week"] = df.index.isocalendar().week.astype(int)
    df["weekday"] = df.index.weekday
    return df


# --- Interaction terms ---
def add_interaction(df, col1, col2):
    df[f"{col1}_x_{col2}"] = df[col1] * df[col2]
    return df
