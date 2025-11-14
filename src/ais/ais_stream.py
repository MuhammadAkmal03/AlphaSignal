import os
import json
import asyncio
import websockets
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
AIS_KEY = os.getenv("AISSTREAM_API_KEY")
if not AIS_KEY:
    raise ValueError("❌ AISSTREAM_API_KEY missing in .env")

# CONFIG
STREAM_TIME = 30        # seconds per port
RAW_DIR = Path("data/raw/ships")
RAW_DIR.mkdir(parents=True, exist_ok=True)

AIS_URI = "wss://stream.aisstream.io/v0/stream"

# PORT LIST (15 GLOBAL HUBS)
PORTS = {
    "Houston": [[29.5, -95.5], [30.0, -94.5]],
    "CorpusChristi": [[27.6, -97.8], [28.0, -97.0]],
    "PortArthur": [[29.6, -94.0], [30.0, -93.7]],

    "Rotterdam": [[51.8, 4.1], [52.0, 4.5]],
    "Antwerp": [[51.2, 4.2], [51.4, 4.5]],
    "Fawley_UK": [[50.8, -1.35], [50.9, -1.25]],

    "Fujairah": [[25.08, 56.30], [25.35, 56.55]],
    "RasTanura": [[26.60, 50.00], [26.90, 50.40]],
    "MinaAlAhmadi": [[29.0, 48.0], [29.4, 48.4]],

    "Singapore": [[1.20, 103.60], [1.35, 104.00]],
    "Qingdao": [[36.00, 120.20], [36.40, 120.80]],
    "Dalian": [[38.70, 121.40], [39.10, 122.00]],
    "Yokohama": [[35.3, 139.5], [35.6, 139.9]],
    "Ulsan": [[35.3, 129.2], [35.7, 129.6]],
    "Mumbai": [[18.8, 72.7], [19.2, 73.0]]
}

# BATCH BUILDER (5 ports per batch)
def create_batches(n=5):
    keys = list(PORTS.keys())
    return [keys[i:i+n] for i in range(0, len(keys), n)]

# STREAM SINGLE PORT (30s)
async def stream_port(port_name, bbox):
    tankers = set()
    print(f"\n== Streaming {port_name} ({STREAM_TIME}s) ==")

    try:
        async with websockets.connect(AIS_URI) as ws:

            # Subscription msg
            sub = {
                "APIKey": AIS_KEY,
                "BoundingBoxes": [bbox],
                "FilterMessageTypes": ["PositionReport"]
            }
            await ws.send(json.dumps(sub))

            start = datetime.now(timezone.utc)
            end = start + timedelta(seconds=STREAM_TIME)

            while datetime.now(timezone.utc) < end:
                # Progress bar
                elapsed = (datetime.now(timezone.utc) - start).seconds
                pct = int(elapsed / STREAM_TIME * 40)
                bar = "[" + "█" * pct + "-" * (40 - pct) + f"] {elapsed}/{STREAM_TIME}s"
                print(bar, end="\r")

                # Receive AIS messages
                try:
                    msg_raw = await asyncio.wait_for(ws.recv(), timeout=2)
                except asyncio.TimeoutError:
                    continue

                msg = json.loads(msg_raw)
                ais = msg.get("Message", {}).get("PositionReport", {})
                if not ais:
                    continue

                mmsi = ais.get("UserID")
                if mmsi:
                    tankers.add(mmsi)

    except Exception as e:
        print(f"\nSTREAM ERROR at {port_name}: {e}")

    print(f"{port_name}: {len(tankers)} tankers")
    return port_name, len(tankers)

# MAIN: RUN ALL BATCHES
async def main():
    batches = create_batches(5)
    results = {}

    for batch in batches:
        print(f"\n=== Running batch: {batch} ===\n")

        tasks = [stream_port(name, PORTS[name]) for name in batch]
        batch_results = await asyncio.gather(*tasks)

        for port, count in batch_results:
            results[port] = count

    # Save output CSV
    today = datetime.utcnow().strftime("%Y-%m-%d")
    row = {"date": today, **results}

    csv_file = RAW_DIR / "ship_counts_per_port.csv"
    df_new = pd.DataFrame([row])

    if csv_file.exists():
        df_old = pd.read_csv(csv_file)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_csv(csv_file, index=False)
    print(f"\nSaved: {csv_file}")

if __name__ == "__main__":
    asyncio.run(main())
