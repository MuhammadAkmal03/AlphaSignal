import os
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load API key
load_dotenv()
EIA_API_KEY = os.getenv("EIA_API_KEY")

RAW_EIA = Path("data/raw/eia")
RAW_EIA.mkdir(parents=True, exist_ok=True)

PRODUCTS = {
    "WTI_Crude": "EPCWTI",
    "NY_Gasoline": "EPMRU",
    "NY_Diesel": "EPD2DXL0"
}

def fetch_eia_data():
    for name, pid in PRODUCTS.items():

        print(f"\nFetching EIA data: {name}")

        url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
        params = {
            "api_key": EIA_API_KEY,
            "frequency": "daily",
            "data[0]": "value",
            "facets[product][]": pid,
            "start": "2015-01-01",
            "end": datetime.utcnow().strftime("%Y-%m-%d"),
            "out": "json"
        }

        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            json_data = r.json()

            # Validate structure
            if "response" not in json_data or "data" not in json_data["response"]:
                print(f" No EIA data found for {name}")
                print(json_data)   # debug
                continue

            df = pd.DataFrame(json_data["response"]["data"])
            df["period"] = pd.to_datetime(df["period"])
            df = df.sort_values("period")
            df.to_csv(RAW_EIA / f"{name}.csv", index=False)

            print(f"Saved: {name}")

        except Exception as e:
            print(f" EIA failed for {name}: {e}")

if __name__ == "__main__":
    fetch_eia_data()
