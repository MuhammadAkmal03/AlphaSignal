# src/data_ingestion.py
import os
import pandas as pd
import yfinance as yf
import requests
import json
import websocket
import threading
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# === CONFIG ===
EIA_API_KEY = os.getenv("EIA_API_KEY")
DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROC_DIR = os.path.join(DATA_DIR, "processed")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROC_DIR, exist_ok=True)
os.makedirs(os.path.join(RAW_DIR, "ships"), exist_ok=True)

# === 1. LOCAL DATASETS (ALREADY DOWNLOADED) ===
def check_local_datasets():
    print("Checking local datasets...")
    satellite_path = os.path.join(RAW_DIR, "satellite")
    transcripts_path = os.path.join(RAW_DIR, "transcripts")
    
    if os.path.exists(satellite_path) and len(os.listdir(satellite_path)) > 100:
        print("Satellite images: FOUND")
    else:
        print("Satellite images: MISSING")
    
    if os.path.exists(transcripts_path) and any(f.endswith(".csv") for f in os.listdir(transcripts_path)):
        print("Earnings transcripts: FOUND")
    else:
        print("Earnings transcripts: MISSING")

# === 2. AISSTREAM.IO: LIVE TANKER COUNT (WITH API KEY) ===
def ingest_aisstream():
    print("Connecting to aisstream.io (authenticated)...")
    API_KEY = os.getenv("AISSTREAM_API_KEY")
    if not API_KEY:
        raise ValueError("AISSTREAM_API_KEY not found in .env")
    
    houston_box = (29.5, 30.0, -95.5, -94.5)
    tankers = []
    all_ships = []
    
    def on_message(ws, message):
        try:
            data = json.loads(message)
            msg_type = data.get("MessageType")
            if msg_type not in [1, 2, 3]:
                return
            
            lat = data.get("Latitude")
            lon = data.get("Longitude")
            ship_type = data.get("VesselType", "")
            mmsi = data.get("MMSI", "unknown")
            
            if not (lat and lon):
                return
            
            all_ships.append({"mmsi": mmsi, "lat": lat, "lon": lon, "type": ship_type, "time": datetime.utcnow().isoformat()})
            
            if (houston_box[0] <= lat <= houston_box[1] and 
                houston_box[2] <= lon <= houston_box[3] and 
                "Tanker" in str(ship_type)):
                tankers.append({"mmsi": mmsi, "lat": lat, "lon": lon, "time": datetime.utcnow().isoformat()})
                print(f"Tanker: MMSI {mmsi} at ({lat:.4f}, {lon:.4f})")
                
        except Exception as e:
            print(f"Parse error: {e}")
    
    def on_open(ws):
        print("Authenticated connection open. Streaming for 60s...")
        threading.Event().wait(60)
        ws.close()
    
    # CONNECT WITH API KEY
    ws_url = f"wss://stream.aisstream.io/v0/stream?api_key={API_KEY}"
    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_open=on_open,
        on_error=lambda ws, err: print(f"WS Error: {err}"),
        on_close=lambda ws, code, msg: print("Stream closed.")
    )
    
    ws.run_forever()
    
    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"{RAW_DIR}/ships/tankers_houston_{timestamp}.json", "w") as f:
        json.dump(tankers, f, indent=2)
    with open(f"{RAW_DIR}/ships/all_ships_{timestamp}.json", "w") as f:
        json.dump(all_ships, f, indent=2)
    
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "houston_tankers_count": len(tankers),
        "total_ships_seen": len(all_ships)
    }
    pd.DataFrame([summary]).to_parquet(f"{PROC_DIR}/ship_summary.parquet", index=False)
    
    print(f"SUCCESS: {len(tankers)} tankers | {len(all_ships)} total ships")
    return summary

# === 3. USO PRICE ===
def ingest_uso_price():
    print("Downloading USO ETF price...")
    df = yf.download("USO", period="2y", progress=False)["Close"].reset_index()
    df.columns = ["date", "close_price"]
    df.to_parquet(f"{PROC_DIR}/uso_price.parquet", index=False)
    df.to_csv(f"{RAW_DIR}/uso_price.csv", index=False)
    print(f"Saved {len(df)} days of USO data")

# === 4. EIA CRACK SPREAD ===
def ingest_eia_crack():
    print("Fetching EIA 3:2:1 Crack Spread...")
    url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
    params = {
        "api_key": EIA_API_KEY,
        "frequency": "weekly",
        "data[0]": "value",
        "facets[series][]": "PET.3_2_1.CRACK.W",
        "start": "2020-01-01",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc"
    }
    try:
        r = requests.get(url, params=params)
        data = r.json()["response"]["data"]
        df = pd.DataFrame(data)[["period", "value"]]
        df["period"] = pd.to_datetime(df["period"])
        df = df.rename(columns={"period": "week_ending", "value": "crack_spread_usd_bbl"})
        df.to_parquet(f"{PROC_DIR}/eia_crack.parquet", index=False)
        df.to_csv(f"{RAW_DIR}/eia_crack.csv", index=False)
        print(f"Saved {len(df)} weeks of EIA data")
    except Exception as e:
        print(f"EIA API failed: {e}")

# === RUN ALL ===
def run_ingestion():
    check_local_datasets()
    summary = ingest_aisstream()
    ingest_uso_price()
    ingest_eia_crack()
    print("\nDATA INGESTION COMPLETE")
    print(f"Tankers near Houston: {summary['houston_tankers_count']}")

if __name__ == "__main__":
    run_ingestion()