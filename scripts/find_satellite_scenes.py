"""Find Sentinel scenes through the public Copernicus STAC catalogue."""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

import requests

from nepal_flood_warning.satellite import SceneQuery, parse_scene_catalog


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="sentinel-2-l2a")
    parser.add_argument("--bbox", nargs=4, type=float, required=True)
    parser.add_argument("--start", type=date.fromisoformat, required=True)
    parser.add_argument("--end", type=date.fromisoformat, required=True)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("scene_catalog.csv"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    query = SceneQuery(args.collection, tuple(args.bbox), args.start, args.end, args.limit)
    response = requests.get(query.url(), timeout=60)
    response.raise_for_status()
    scenes = parse_scene_catalog(response.json())
    scenes.sort(key=lambda row: (row["cloud_cover_pct"] is None, row["cloud_cover_pct"] or 999))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=scenes[0].keys() if scenes else [])
        if scenes:
            writer.writeheader()
            writer.writerows(scenes)
    print(f"Wrote {len(scenes)} scenes to {args.output}")


if __name__ == "__main__":
    main()

