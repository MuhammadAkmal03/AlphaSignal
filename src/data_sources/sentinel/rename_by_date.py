import json
from pathlib import Path
import shutil
from datetime import datetime

RAW = Path("data/raw/sentinel")
OUT = Path("data/raw/sentinel_dated")
OUT.mkdir(parents=True, exist_ok=True)


def extract_date(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)

    # sentinelhub sometimes returns date in different fields
    # we check all possible locations
    candidates = []

    def search(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    search(v)
                if isinstance(v, str) and "T" in v and v.endswith("Z"):
                    try:
                        candidates.append(datetime.fromisoformat(v.replace("Z", "+00:00")))
                    except:
                        pass
        elif isinstance(obj, list):
            for item in obj:
                search(item)

    search(data)

    if not candidates:
        return None

    # choose earliest timestamp
    return min(candidates).strftime("%Y-%m-%d")


def run():
    print("\n=== Renaming Sentinel Images with True Dates ===\n")

    for refinery_folder in RAW.iterdir():
        if not refinery_folder.is_dir():
            continue

        print(f"\nRefinery: {refinery_folder.name}")

        out_ref = OUT / refinery_folder.name
        out_ref.mkdir(parents=True, exist_ok=True)

        for request_folder in refinery_folder.iterdir():
            if not request_folder.is_dir():
                continue

            json_file = request_folder / "request.json"
            img_file = request_folder / "response.png"

            if not json_file.exists() or not img_file.exists():
                continue

            date_str = extract_date(json_file)
            if not date_str:
                print(f"  Could not extract date from {json_file}")
                continue

            new_name = out_ref / f"{date_str}.png"
            shutil.copy(img_file, new_name)
            print(f"  Saved → {new_name}")

    print("\nDONE — Images renamed with correct dates!")


if __name__ == "__main__":
    run()
