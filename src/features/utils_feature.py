import pandas as pd
import numpy as np

def add_lag_features(df, col, lags=[1, 3, 7, 14, 30]):
    for lag in lags:
        df[f"{col}_lag_{lag}"] = df[col].shift(lag)
    return df

def add_rolling_features(df, col):
    df[f"{col}_7ma"] = df[col].rolling(7).mean()
    df[f"{col}_30ma"] = df[col].rolling(30).mean()
    df[f"{col}_vol_30"] = df[col].rolling(30).std()
    return df

def add_date_features(df):
    df["year"] = df.index.year
    df["month"] = df.index.month
    df["week"] = df.index.isocalendar().week
    df["weekday"] = df.index.weekday
    return df

def add_interaction(df, col1, col2):
    df[f"{col1}_x_{col2}"] = df[col1] * df[col2]
    return df
