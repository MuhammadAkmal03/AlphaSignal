import shutil
from pathlib import Path

SENTINEL_ROOT = Path("data/raw/sentinel")
OUT = Path("data/raw/sentinel_images")
OUT.mkdir(parents=True, exist_ok=True)

def extract_images():
    folders = list(SENTINEL_ROOT.rglob("*"))
    count = 0

    for f in folders:
        img = f / "response.png"
        if img.exists():
            # Create unique filename
            new_name = f"{f.name}.png"
            dst = OUT / new_name
            shutil.copy(img, dst)
            count += 1

    print(f"Extracted {count} Sentinel images → {OUT}")

if __name__ == "__main__":
    extract_images()
