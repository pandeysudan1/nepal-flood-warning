"""Download preview JPEGs listed in a scene catalogue CSV."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import requests


def safe_name(scene_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", scene_id)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("scene_previews"))
    parser.add_argument("--maximum", type=int, default=3)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with args.catalog.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    downloaded = 0
    for row in rows:
        url = row.get("thumbnail_url")
        if not url or downloaded >= args.maximum:
            continue
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        destination = args.output_dir / f"{safe_name(row['scene_id'])}.jpg"
        destination.write_bytes(response.content)
        downloaded += 1
        print(destination)


if __name__ == "__main__":
    main()

