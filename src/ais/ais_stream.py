import os
import json
import asyncio
import websockets
import pandas as pd
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

AISSTREAM_API_KEY = os.getenv("AISSTREAM_API_KEY")
if not AISSTREAM_API_KEY:
    raise ValueError("Missing AISSTREAM_API_KEY in .env")

PORTS = {
    "Houston": [[29.5, -95.5], [30.0, -94.5]],
    "Singapore": [[1.1, 103.6], [1.42, 104.0]],
    "Rotterdam": [[51.8, 4.1], [52.0, 4.5]],
    "Fujairah": [[25.0, 56.2], [25.3, 56.5]],
    "RasTanura": [[26.4, 49.9], [26.8, 50.3]],
    "Antwerp": [[51.2, 4.2], [51.4, 4.5]],
    "Qingdao": [[35.9, 120.1], [36.3, 120.6]],
    "Dalian": [[38.8, 121.3], [39.2, 121.8]],
    "CorpusChristi": [[27.6, -97.8], [27.95, -97.2]],
    "PortArthur": [[29.7, -94.0], [29.95, -93.6]],
    "Fawley_UK": [[50.8, -1.4], [51.0, -1.2]],
    "MinaAlAhmadi": [[29.0, 48.1], [29.3, 48.4]],
    "Yokohama": [[35.3, 139.5], [35.6, 139.9]],
    "Ulsan": [[35.4, 129.2], [35.7, 129.5]],
    "Mumbai": [[18.8, 72.7], [19.2, 73.1]],
}

RAW = Path("data/raw/ships")
EXISTDATA_PATH = RAW / "s_ship_counts.csv"


# Stream a single port for 30 seconds
async def stream_port(port, bbox):
    uri = "wss://stream.aisstream.io/v0/stream"
    tanker_mmsi = set()
    start = datetime.now(timezone.utc)
    end = start + timedelta(seconds=30)

    try:
        async with websockets.connect(uri) as ws:
            sub = {
                "APIKey": AISSTREAM_API_KEY,
                "BoundingBoxes": [bbox],
                "FilterMessageTypes": ["PositionReport"]
            }
            await ws.send(json.dumps(sub))

            while datetime.now(timezone.utc) < end:
                try:
                    msg_raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
                except asyncio.TimeoutError:
                    continue

                msg = json.loads(msg_raw)
                ais = msg.get("Message", {}).get("PositionReport", {})
                if ais:
                    tanker_mmsi.add(ais.get("UserID"))

    except Exception as e:
        print(f"Stream error at {port}: {e}")

    return port, len(tanker_mmsi)


# Run streaming for all ports sequentially
async def stream_all_ports():
    results = {}
    for port, bbox in PORTS.items():
        print(f"\n== Streaming {port} (30s) ==\n")
        p, cnt = await stream_port(port, bbox)
        results[p] = cnt
        print(f"{port}: {cnt} tankers")

    return results


# Merge data into existing dataset
def merge_into_synthetic(real_counts):
    df = pd.read_csv(EXISTDATA_PATH)

    # ALWAYS keep YYYY-MM-DD format only
    df["date"] = df["date"].astype(str).str.slice(0, 10)

    today = datetime.utcnow().strftime("%Y-%m-%d")

    # If today exists, overwrite. If not, append row.
    if today in df["date"].values:
        idx = df.index[df["date"] == today][0]
        print(f"\nUpdating existing row for {today}")
    else:
        print(f"\nAppending new row for {today}")
        df.loc[len(df)] = [today] + [0] * (len(df.columns)-1)
        idx = df.index[-1]

    print("\n== Merging real data ==")
    for port, real_value in real_counts.items():
        synthetic_value = df.loc[idx, port]
        if real_value > 0:
            df.loc[idx, port] = real_value
            print(f"{port}: {synthetic_value} → {real_value} (updated)")
        else:
            print(f"{port}: kept synthetic {synthetic_value} (real=0)")

    df.to_csv(EXISTDATA_PATH, index=False)
    print("\nMerge complete! Today's AIS data saved.")


if __name__ == "__main__":
    print("\n=== Daily AIS Data Update (30s per port) ===\n")
    real_counts = asyncio.run(stream_all_ports())
    merge_into_synthetic(real_counts)
