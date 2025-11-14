import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

from sentinelhub import (
    SHConfig,
    SentinelHubRequest,
    DataCollection,
    BBox,
    CRS,
    MimeType
)

# Load .env Credentials

load_dotenv()

config = SHConfig()
config.sh_client_id = os.getenv("SH_CLIENT_ID")
config.sh_client_secret = os.getenv("SH_CLIENT_SECRET")

if not config.sh_client_id or not config.sh_client_secret:
    raise ValueError("Missing SentinelHub credentials in .env")


#  Save Directory

SAVE_DIR = Path("data/raw/sentinel")
SAVE_DIR.mkdir(parents=True, exist_ok=True)


#  40 Fully Verified Refineries / Storage Hubs

REFINERIES = [
    ("Houston – USA", 29.7283, -95.1330),
    ("Port Arthur – USA", 29.8554, -93.9390),
    ("Beaumont – USA", 30.0865, -94.0840),
    ("Lake Charles – USA", 30.1240, -93.2260),
    ("Baton Rouge – USA", 30.4413, -91.2300),
    ("New Orleans – USA", 29.9590, -90.4220),
    ("Corpus Christi – USA", 27.8170, -97.4330),
    ("St Charles – USA", 29.9490, -90.3250),
    ("Los Angeles – USA", 33.7644, -118.2080),
    ("Martinez – USA", 38.0180, -122.1180),
    ("Anacortes – USA", 48.5020, -122.6070),
    ("Cushing – USA", 35.9850, -96.7570),

    ("Ras Tanura – Saudi Arabia", 26.6430, 50.0700),
    ("Jubail – Saudi Arabia", 27.0170, 49.5990),
    ("Yanbu – Saudi Arabia", 24.0890, 38.0630),
    ("Rabigh – Saudi Arabia", 22.8060, 39.0400),

    ("Fujairah – UAE", 25.1650, 56.3580),
    ("Ruwais – UAE", 24.0910, 52.7290),
    ("Jebel Ali – UAE", 25.0000, 55.1100),

    ("Jamnagar – India", 22.3260, 69.8920),
    ("Vadinar – India", 22.4530, 69.6580),
    ("Mumbai – India", 19.0510, 72.8560),
    ("Chennai – India", 13.1440, 80.3020),
    ("Kochi – India", 9.9790, 76.2800),

    ("Qingdao – China", 36.0900, 120.3210),
    ("Dalian – China", 38.9550, 121.5780),
    ("Tianjin – China", 38.9570, 117.7730),
    ("Shanghai – China", 30.6570, 121.3170),
    ("Ningbo – China", 29.8560, 121.6010),
    ("Zhuhai – China", 22.0040, 113.4100),
    ("Guangzhou – China", 23.0800, 113.4600),

    ("Yokohama – Japan", 35.4630, 139.6680),
    ("Chiba – Japan", 35.6050, 140.0430),
    ("Kawasaki – Japan", 35.5200, 139.7500),

    ("Ulsan – Korea", 35.5000, 129.3640),
    ("Yosu – Korea", 34.8340, 127.7120),
    ("Busan – Korea", 35.0970, 129.0420),

    ("Jurong – Singapore", 1.2940, 103.7890),
    ("Rotterdam – Netherlands", 51.8850, 4.2890),
    ("Antwerp – Belgium", 51.2850, 4.2850),
    ("Huelva – Spain", 37.2580, -6.9480),
    ("Sines – Portugal", 37.9550, -8.7950),
    ("Milford Haven – UK", 51.7140, -5.0500),
]


# Evalscript for True Color

TRUE_COLOR = """
let rgb = [B04, B03, B02];
return rgb.map(x => x * 3.0);
"""


#  Monthly Date Ranges

def month_ranges():
    end = datetime.utcnow().replace(day=1)
    months = []
    for i in range(12):
        month_end = end - timedelta(days=1)
        month_start = month_end.replace(day=1)
        months.append((month_start, month_end))
        end = month_start
    return list(reversed(months))


#  Download One Month of Imagery per Refinery

def fetch_month(name, lat, lon, ms, me):
    print(f"   → {name} ({ms} → {me})")

    path = SAVE_DIR / name.replace(" ", "_")
    path.mkdir(parents=True, exist_ok=True)

    bbox = BBox([lon - 0.03, lat - 0.03, lon + 0.03, lat + 0.03], crs=CRS.WGS84)

    req = SentinelHubRequest(
        evalscript=TRUE_COLOR,
        data_folder=str(path),
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=(ms, me),
                maxcc=0.20,
                mosaicking_order="leastCC"
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=bbox,
        size=(1024, 1024),
        config=config
    )

    try:
        data = req.get_data(save_data=True)
        print(f" saved {len(data)} img")
    except Exception as e:
        print(f" Error: {e}")



# main function

def download_sentinel_images():
    print("\n========== Sentinel Refinery Download (40 Verified Sites) ==========\n")

    months = month_ranges()

    for name, lat, lon in REFINERIES:
        print(f"\n {name}")
        for start_dt, end_dt in months:
            ms = start_dt.strftime("%Y-%m-%d")
            me = end_dt.strftime("%Y-%m-%d")
            fetch_month(name, lat, lon, ms, me)

    print("\n DONE — Images saved in:", SAVE_DIR)

# run

if __name__ == "__main__":
    download_sentinel_images()
