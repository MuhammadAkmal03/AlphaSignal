import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from ultralytics import YOLO

MODEL_PATH = "weights/yolov8l.pt"

IMAGE_DIR = Path("data/raw/sentinel_dated")

OUTPUT = Path("data/processed")
OUTPUT.mkdir(parents=True, exist_ok=True)

def parse_date(img_path):
    """
    Extracts date from filename ONLY:
    Example: '2025-05-01.png' → 2025-05-01
    """
    filename = img_path.name               # e.g. Dalian__China/2025-05-01.png
    date_str = filename.split(".")[0]      # → "2025-05-01"

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        print("Skipping invalid filename:", filename)
        return None


def compute_fullness(avg_conf):
    """
    Convert YOLO detections → fullness %
    """
    if avg_conf <= 0.20:
        regime = "Low"
        fullness = 35 + avg_conf * 50
    elif avg_conf <= 0.50:
        regime = "Mid"
        fullness = 55 + (avg_conf - 0.2) * 40
    else:
        regime = "High"
        fullness = 70 + (avg_conf - 0.5) * 30

    return min(100, max(0, fullness)), regime


def main():
    print("\n=== Tank Fullness Estimation using YOLOv8 ===\n")

    model = YOLO(MODEL_PATH)

    rows = []

    for refinery_dir in IMAGE_DIR.iterdir():
        if not refinery_dir.is_dir():
            continue

        print(f"\nProcessing refinery: {refinery_dir.name}")

        for img_path in refinery_dir.glob("*.png"):
            date = parse_date(img_path)
            if date is None:
                continue

            # run YOLO
            results = model(img_path)

            confs = []
            for r in results:
                for box in r.boxes:
                    confs.append(float(box.conf.cpu()))

            if len(confs) == 0:
                avg_conf = 0
            else:
                avg_conf = sum(confs) / len(confs)

            fullness_pct, regime = compute_fullness(avg_conf)

            rows.append({
                "date": date,
                "refinery": refinery_dir.name,
                "fullness_pct": round(fullness_pct, 2),
                "regime": regime
            })

    if len(rows) == 0:
        print(" No data processed!")
        return

    df = pd.DataFrame(rows).sort_values("date")
    out_path = OUTPUT / "tank_fullness_yolo.csv"
    df.to_csv(out_path, index=False)

    print("\nSaved tank fullness →", out_path)


if __name__ == "__main__":
    main()
