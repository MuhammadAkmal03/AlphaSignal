import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# ------- CONFIG -------
YOLO_CSV = Path("data/processed/tank_fullness_yolo.csv")   
MASTER_IN = Path("data/processed/master_dataset_with_fullness.csv")    
MASTER_CLEAN_OUT = Path("data/final/master_dataset_with_tankfullness.csv")
DATE_COL = "date"
YOLO_DATE_FORMATS = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]  
# mapping from YOLO site naming to master column names (if needed)
SITE_TO_MASTER_COL = {
    # example entries — add any variations you use so names align with master
    "Houston_–_USA": "Houston",
    "Houston_–_USA": "Houston",
    "Houston_–_USA": "Houston",
    "Antwerp_–_Belgium": "Antwerp",
    "Qingdao_–_China": "Qingdao",
    "Dalian_–_China": "Dalian",
    "Mumbai_–_India": "Mumbai",
    
}


# ------- UTIL -------
def parse_date(s):
    if pd.isna(s):
        return None
    s = str(s).strip()
    # remove windows/backslash stray prefixes like 'China\\2025-05-01'
    if "\\" in s:
        s = s.split("\\")[-1]
    if "/" in s:
        s = s.replace("/", "-")
    for fmt in YOLO_DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            continue
    # fallback: try pandas
    try:
        return pd.to_datetime(s).date()
    except Exception:
        raise ValueError(f"Unparseable date: {s}")

def normalize_site(name):
    if pd.isna(name):
        return name
    n = str(name).strip()
    # unify unicode hyphen/dash variants
    n = n.replace("–", "-")  # normalize long dash to single char (optional)
    # strip spaces
    n = n.replace(" ", "_")
    # try mapping
    if n in SITE_TO_MASTER_COL:
        return SITE_TO_MASTER_COL[n]
    # simple heuristics: drop country suffix after last underscore/dash
    # e.g., "Houston_–_USA" -> "Houston"
    for sep in ["_", "-", "-"]:
        if sep in n:
            candidate = n.split(sep)[0]
            if candidate:
                return candidate
    return n

# ------- MAIN -------
def main():
    print("\n=== Merge YOLO Tank Fullness into Master Dataset ===\n")

    if not YOLO_CSV.exists():
        raise FileNotFoundError(f"YOLO CSV not found: {YOLO_CSV}")

    if not MASTER_IN.exists():
        raise FileNotFoundError(f"Master dataset not found: {MASTER_IN}")

    # load YOLO
    df_y = pd.read_csv(YOLO_CSV)
    print(f" YOLO rows loaded: {len(df_y)}")

    # normalize and parse
    rows = []
    for _, r in df_y.iterrows():
        try:
            d = parse_date(r.get("date", None))
        except Exception as e:
            print(f" Error parsing date for row {r.to_dict()}: {e}")
            continue
        site_norm = normalize_site(r.get("site", r.get("Site", r.get("refinery", ""))))
        try:
            fullness = float(r.get("fullness", r.get("fullness_pct", r.get("tank_fullness_global_pct", None))))
        except Exception:
            fullness = None
        rows.append({"date": pd.to_datetime(d), "site": site_norm, "fullness": fullness})

    df_y2 = pd.DataFrame(rows).dropna(subset=["date"])
    if df_y2.empty:
        raise ValueError("No usable YOLO rows after parsing.")
    # compute per-date global mean fullness (mean across sites)
    df_ag = df_y2.groupby("date", as_index=False)["fullness"].mean().rename(columns={"fullness": "tank_fullness_global_pct"})
    print(f" YOLO dates aggregated: {len(df_ag)}")

    # load master
    df_master = pd.read_csv(MASTER_IN)
    if DATE_COL not in df_master.columns:
        # try other common names
        if "Date" in df_master.columns:
            df_master.rename(columns={"Date": "date"}, inplace=True)
        else:
            raise KeyError("Master dataset missing a 'date' column")

    df_master["date"] = pd.to_datetime(df_master["date"]).dt.date

    # merge (left join so we keep master index)
    df_ag["date"] = pd.to_datetime(df_ag["date"]).dt.date
    df_merged = pd.merge(df_master, df_ag, on="date", how="left")

    # What column to create/update? use 'tank_inventory_score' as existing pipeline expects it.
    # If master already had a tank_inventory_score column, keep old as _old and overwrite where YOLO exists.
    if "tank_inventory_score" in df_merged.columns:
        df_merged.rename(columns={"tank_inventory_score": "tank_inventory_score_old"}, inplace=True)

    # create new column
    df_merged["tank_inventory_score"] = df_merged["tank_fullness_global_pct"]

    # if no YOLO value for a date, fallback to old column if exists, else leave NaN
    if "tank_inventory_score_old" in df_merged.columns:
        df_merged["tank_inventory_score"] = df_merged["tank_inventory_score"].fillna(df_merged["tank_inventory_score_old"])

    # forward/back fill to cover monthly->daily gaps (only if you want to propagate monthly to daily)
    # NOTE: choose strategy: ffill is used to propagate last observed monthly value forward.
    df_merged = df_merged.sort_values("date")
    # convert date back to datetime for saving
    df_merged["date"] = pd.to_datetime(df_merged["date"])
    df_merged["tank_inventory_score"] = df_merged["tank_inventory_score"].ffill().bfill()

    # save
    MASTER_CLEAN_OUT.parent.mkdir(parents=True, exist_ok=True)
    df_merged.to_csv(MASTER_CLEAN_OUT, index=False)
    print(f"\nMerged master saved to: {MASTER_CLEAN_OUT}")
    print("Done.\n")

if __name__ == "__main__":
    main()
