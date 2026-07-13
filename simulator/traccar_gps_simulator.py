"""
Traccar GPS Trip Simulator — makes trucks "online" and generates real trip
history so /reports/trips returns actual data instead of empty arrays.

WHY YOU NEED THIS:
Your 5 Traccar devices show "Offline" because no GPS hardware has ever sent
them a position. Traccar has no data to report on until a device (real or
simulated) pushes at least 2 position points. This script pushes a start
point and an end point (plus a few in-between) for each truck along a real
route, timestamped to match your Form_Responses test data, so Workflow 1
gets non-empty trips to reconcile against.

PROTOCOL:
Traccar's OsmAnd HTTP protocol is the simplest way to inject positions
without real hardware. Default port is 5055, but hosted/hosted-demo Traccar
instances sometimes proxy this behind a different port or path. If this
script gets connection errors, log into the Traccar UI as this instance's
admin and check Settings > Server (or ask whoever provisioned
x5mwdk7xw.traccar.com) which ports are open for inbound protocols — cloud
Traccar demo accounts commonly restrict which client protocols are enabled.

USAGE:
  pip install requests
  python3 traccar_gps_simulator.py

Edit TRUCKS below to match your real device uniqueIds (already filled in
from the device list you pulled: IMEI_TRUCK_1 .. IMEI_TRUCK_5).
"""

import requests
import time
from datetime import datetime, timedelta, timezone

# Traccar OsmAnd protocol endpoint. CHANGE THE PORT if 5055 doesn't work —
# see note above.
TRACCAR_HOST = "x5mwdk7xw.traccar.com"
OSMAND_PORT = 5055
OSMAND_URL = f"http://78.46.203.92:{OSMAND_PORT}"

# Real uniqueIds pulled from your /api/devices response
TRUCKS = [
    {"uniqueId": "IMEI_TRUCK_1", "truck_id": "TRK-001"},
    {"uniqueId": "IMEI_TRUCK_2", "truck_id": "TRK-002"},
    {"uniqueId": "IMEI_TRUCK_3", "truck_id": "TRK-003"},
    {"uniqueId": "IMEI_TRUCK_4", "truck_id": "TRK-004"},
    {"uniqueId": "IMEI_TRUCK_5", "truck_id": "TRK-005"},
]

# Lahore -> Karachi corridor waypoints (approx, matches Master_Routes RT-01).
# Distance along this path ~1220km, matching your Config/Master_Routes data.
ROUTE_LAHORE_KARACHI = [
    (31.5497, 74.3436),  # Lahore Depot
    (30.1575, 71.5249),  # Multan
    (28.4212, 70.3298),  # Rahim Yar Khan
    (27.7244, 68.8272),  # Sukkur
    (25.3960, 68.3578),  # Hyderabad
    (24.8607, 67.0011),  # Karachi Terminal
]


def send_position(unique_id, lat, lon, speed_knots, ts, ignition=True):
    params = {
        "id": unique_id,
        "lat": lat,
        "lon": lon,
        "timestamp": int(ts.timestamp()),
        "speed": speed_knots,
        "ignition": str(ignition).lower(),
    }
    try:
        r = requests.get(OSMAND_URL, params=params, timeout=10)
        print(f"[{unique_id}] {ts.isoformat()} lat={lat} lon={lon} -> HTTP {r.status_code}")
        return r.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"[{unique_id}] FAILED: {e}")
        return False


def simulate_trip(truck, trip_date, start_hour=6, duration_hours=17, avg_speed_kmh=72):
    """
    Sends one position per waypoint, spaced out across duration_hours,
    matching a single day's trip so Traccar's /reports/trips returns
    exactly one trip for this device/date.
    """
    start_ts = datetime(trip_date.year, trip_date.month, trip_date.day,
                         start_hour, 0, 0, tzinfo=timezone.utc)
    step = timedelta(hours=duration_hours) / (len(ROUTE_LAHORE_KARACHI) - 1)
    speed_knots = round(avg_speed_kmh / 1.852, 1)

    for i, (lat, lon) in enumerate(ROUTE_LAHORE_KARACHI):
        ts = start_ts + step * i
        # ignition off at the very last point to close the trip cleanly
        ignition = i < len(ROUTE_LAHORE_KARACHI) - 1
        send_position(truck["uniqueId"], lat, lon, speed_knots, ts, ignition)
        time.sleep(0.3)


if __name__ == "__main__":
    # Match this to your Form_Responses Trip_Start_Date test rows.
    trip_date = datetime(2026, 7, 2)

    print(f"Simulating trips for {len(TRUCKS)} trucks on {trip_date.date()}...")
    for truck in TRUCKS:
        print(f"\n--- {truck['truck_id']} ({truck['uniqueId']}) ---")
        simulate_trip(truck, trip_date)

    print("\nDone. Check Traccar UI -> Reports -> Trips for each device to confirm.")
    print("If devices still show 'Offline' in the sidebar, that's normal for the")
    print("OsmAnd protocol (it doesn't hold a persistent socket) — what matters")
    print("is whether Reports > Trips now shows a trip for the date above.")
