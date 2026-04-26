import argparse
import random
import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import httpx

EVENT_TEMPLATES = [
    {
        "event_type": "STOPPED_VEHICLE",
        "camera_id": "CAM-TOMEI-001",
        "highway_id": "E1",
        "latitude": 35.4359,
        "longitude": 139.3862,
        "description": "Vehicle stopped in a live lane near an interchange merge.",
    },
    {
        "event_type": "DEBRIS",
        "camera_id": "CAM-CHUO-014",
        "highway_id": "E20",
        "latitude": 35.6527,
        "longitude": 139.4872,
        "description": "Road debris detected on the shoulder and partially intruding into lane one.",
    },
    {
        "event_type": "CONGESTION",
        "camera_id": "CAM-C2-022",
        "highway_id": "C2",
        "latitude": 35.6901,
        "longitude": 139.7414,
        "description": "Abnormal low-speed traffic cluster forming in the monitored segment.",
    },
]

SEVERITY_OPTIONS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def build_payload() -> dict:
    template = random.choice(EVENT_TEMPLATES)
    detected_at = datetime.now(timezone.utc) - timedelta(seconds=random.randint(2, 20))

    return {
        **template,
        "source_event_id": f"seed-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')}-{uuid4().hex[:8]}",
        "severity": random.choices(SEVERITY_OPTIONS, weights=[1, 2, 3, 2], k=1)[0],
        "confidence": round(random.uniform(0.6, 0.99), 2),
        "image_url": f"https://picsum.photos/seed/{random.randint(1000, 9999)}/640/360",
        "detected_at": detected_at.isoformat(),
        "road_marker": f"K{random.randint(1, 80)}+{random.randint(0, 999):03d}",
        "lane_no": str(random.randint(1, 3)),
        "extra_payload": {"generator": "seed.py"},
    }


def main():
    parser = argparse.ArgumentParser(description="Continuously post random traffic incidents.")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Target API base URL")
    parser.add_argument("--count", type=int, default=0, help="Number of incidents to send. Use 0 for infinite.")
    parser.add_argument("--min-delay", type=float, default=2.0, help="Minimum seconds between requests")
    parser.add_argument("--max-delay", type=float, default=5.0, help="Maximum seconds between requests")
    args = parser.parse_args()

    infinite = args.count <= 0
    remaining = args.count
    with httpx.Client(timeout=10.0) as client:
        while infinite or remaining > 0:
            payload = build_payload()
            try:
                response = client.post(f"{args.base_url}/events", json=payload)
                response.raise_for_status()
                incident = response.json()["data"]
                print(
                    f"[{datetime.now().isoformat(timespec='seconds')}] "
                    f"created {incident['id']} {incident['event_type']} {incident['severity']}"
                )
                if not infinite:
                    remaining -= 1
            except httpx.HTTPError as exc:
                print(f"[{datetime.now().isoformat(timespec='seconds')}] seed request failed: {exc}")

            time.sleep(random.uniform(args.min_delay, args.max_delay))


if __name__ == "__main__":
    main()
