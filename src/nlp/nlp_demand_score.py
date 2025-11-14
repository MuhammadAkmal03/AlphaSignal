import os
import pandas as pd
from transformers import pipeline
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# NLP model
nlp = pipeline("sentiment-analysis")

# raw directory
RAW_ECT = Path("data/raw/ECT/cleaned_ECTs_dataset")
RAW_ECT.mkdir(parents=True, exist_ok=True)

OUTPUT = Path("data/processed")
OUTPUT.mkdir(parents=True, exist_ok=True)


def extract_date_from_filename(fname: str):
    """
    Example filename:
      2019_Q3_acn_processed.txt
    """
    try:
        year = fname.split("_")[0]
        quarter = fname.split("_")[1]  # e.g., Q3
        month = {"Q1": "03", "Q2": "06", "Q3": "09", "Q4": "12"}[quarter]
        return f"{year}-{month}-01"
    except:
        return datetime.utcnow().strftime("%Y-%m-%d")


def generate_demand_score():

    txt_files = list(RAW_ECT.rglob("*.txt"))
    rows = []

    keywords = {"demand", "supply", "refining", "inventory",
                "crude", "diesel", "gasoline", "oil", "energy"}

    print(f"\nFound {len(txt_files)} transcript files.\n")

    for fp in txt_files:
        text = fp.read_text(errors="ignore").lower()

        # Keep only keyword-related words (signal extraction)
        filtered = " ".join(w for w in text.split() if w in keywords)
        filtered = filtered[:512]  # BERT token limit

        if not filtered.strip():
            continue

        sentiment = nlp(filtered)[0]

        score = sentiment["score"] if sentiment["label"] == "POSITIVE" else -sentiment["score"]

        date_str = extract_date_from_filename(fp.name)

        rows.append({
            "date": date_str,
            "company": fp.parent.name,
            "file": fp.name,
            "demand_score": score
        })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.groupby("date")["demand_score"].mean().reset_index()

    out_path = OUTPUT / "demand_score.csv"
    df.to_csv(out_path, index=False)

    print("\n NLP demand_score.csv saved!")
    print("Location:", out_path)


if __name__ == "__main__":
    generate_demand_score()
