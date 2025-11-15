import pandas as pd

df = pd.read_csv("data/processed/master_dataset.csv")

# Fix date
df["date"] = pd.to_datetime(df["date"])

# Replace empty strings with NaN
df.replace("", None, inplace=True)

# Forward fill missing values
df = df.ffill().bfill()

# Deduplicate by date
df = df.groupby("date", as_index=False).mean(numeric_only=True)

# Save clean version
df.to_csv("data/processed/master_dataset_clean.csv", index=False)

print("Master dataset cleaned & saved!")
