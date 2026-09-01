"""Satellite scene discovery and an interpretable daily GLOF watch index.

The watch index is a screening tool, not a calibrated event probability.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any
from urllib.parse import urlencode

CDSE_STAC_ENDPOINT = "https://stac.dataspace.copernicus.eu/v1"


@dataclass(frozen=True)
class SceneQuery:
    """Query parameters for the Copernicus Data Space STAC catalogue."""

    collection: str
    bbox: tuple[float, float, float, float]
    start: date
    end: date
    limit: int = 20

    def validate(self) -> None:
        west, south, east, north = self.bbox
        if west >= east or south >= north:
            raise ValueError("bbox must be ordered west, south, east, north")
        if self.start > self.end:
            raise ValueError("start date cannot be after end date")
        if not 1 <= self.limit <= 100:
            raise ValueError("limit must be between 1 and 100")

    def url(self) -> str:
        self.validate()
        params = urlencode(
            {
                "bbox": ",".join(str(value) for value in self.bbox),
                "datetime": f"{self.start.isoformat()}T00:00:00Z/{self.end.isoformat()}T23:59:59Z",
                "limit": self.limit,
            },
            safe=",/:T",
        )
        return f"{CDSE_STAC_ENDPOINT}/collections/{self.collection}/items?{params}"


def parse_scene_catalog(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract the small metadata table needed for scene selection."""
    scenes = []
    for feature in payload.get("features", []):
        properties = feature.get("properties", {})
        assets = feature.get("assets", {})
        scenes.append(
            {
                "scene_id": feature.get("id"),
                "datetime": properties.get("datetime"),
                "cloud_cover_pct": properties.get("eo:cloud_cover"),
                "platform": properties.get("platform"),
                "thumbnail_url": assets.get("thumbnail", {}).get("href"),
                "collection": feature.get("collection"),
            }
        )
    return scenes


@dataclass(frozen=True)
class DailyGlacierFeatures:
    """Daily inputs for a lake-level screening index."""

    lake_area_growth_30d_pct: float
    precipitation_24h_mm: float
    precipitation_72h_mm: float
    positive_degree_days_7d: float
    snow_fraction_change_7d: float
    sar_change_db: float
    static_hazard: float
    missing_fraction: float = 0.0
    optical_age_days: float = 0.0
    sar_age_days: float = 0.0

    def validate(self) -> None:
        if min(self.precipitation_24h_mm, self.precipitation_72h_mm) < 0:
            raise ValueError("precipitation cannot be negative")
        if not 0 <= self.static_hazard <= 1:
            raise ValueError("static_hazard must be between 0 and 1")
        if not 0 <= self.missing_fraction <= 1:
            raise ValueError("missing_fraction must be between 0 and 1")
        if min(self.optical_age_days, self.sar_age_days) < 0:
            raise ValueError("observation age cannot be negative")


@dataclass(frozen=True)
class RiskAssessment:
    score: float
    band: str
    confidence: float
    drivers: tuple[str, ...]


def _scaled(value: float, reference: float, weight: float) -> float:
    return min(max(value, 0.0) / reference, 1.0) * weight


def screen_daily_risk(features: DailyGlacierFeatures) -> RiskAssessment:
    """Calculate a transparent 0-100 watch index and data confidence.

    Thresholds are engineering placeholders. They require calibration against
    regional event and non-event records before any warning use.
    """
    features.validate()
    components = {
        "rapid lake-area growth": _scaled(features.lake_area_growth_30d_pct, 25, 25),
        "24-hour precipitation": _scaled(features.precipitation_24h_mm, 50, 15),
        "72-hour precipitation": _scaled(features.precipitation_72h_mm, 150, 15),
        "seven-day melt energy": _scaled(features.positive_degree_days_7d, 70, 15),
        "seven-day snow loss": _scaled(-features.snow_fraction_change_7d, 0.5, 10),
        "SAR surface change": _scaled(abs(features.sar_change_db), 4, 10),
        "static lake hazard": features.static_hazard * 10,
    }
    score = round(sum(components.values()), 1)
    if score >= 70:
        band = "high watch"
    elif score >= 45:
        band = "elevated watch"
    elif score >= 25:
        band = "watch"
    else:
        band = "baseline"

    freshness = min(1.0, 7 / max(features.optical_age_days, 7))
    freshness *= min(1.0, 12 / max(features.sar_age_days, 12))
    confidence = round((1 - features.missing_fraction) * freshness, 2)
    drivers = tuple(name for name, value in components.items() if value >= 0.6 * 10)
    return RiskAssessment(score=score, band=band, confidence=confidence, drivers=drivers)

