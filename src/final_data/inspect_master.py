import pandas as pd

df = pd.read_csv("data/processed/master_dataset.csv", parse_dates=["date"])

print("\n=== HEAD ===")
print(df.head())

print("\n=== INFO ===")
print(df.info())

print("\n=== DESCRIBE ===")
print(df.describe())
