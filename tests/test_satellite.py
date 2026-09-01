from datetime import date

import pytest

from nepal_flood_warning.satellite import (
    DailyGlacierFeatures,
    SceneQuery,
    parse_scene_catalog,
    screen_daily_risk,
)


def test_scene_query_contains_collection_bbox_and_dates():
    query = SceneQuery(
        "sentinel-2-l2a",
        (86.85, 27.85, 87.0, 28.0),
        date(2026, 4, 1),
        date(2026, 4, 30),
    )
    url = query.url()
    assert "/collections/sentinel-2-l2a/items?" in url
    assert "bbox=86.85,27.85,87.0,28.0" in url
    assert "2026-04-01T00:00:00Z/2026-04-30T23:59:59Z" in url


def test_scene_query_rejects_bad_bbox():
    with pytest.raises(ValueError, match="bbox"):
        fixed_date = date(2026, 4, 1)
        SceneQuery("sentinel-1-grd", (87, 28, 86, 27), fixed_date, fixed_date).url()


def test_parse_scene_catalog_extracts_thumbnail():
    payload = {
        "features": [
            {
                "id": "scene-1",
                "collection": "sentinel-2-l2a",
                "properties": {"datetime": "2026-04-11T00:00:00Z", "eo:cloud_cover": 0.3},
                "assets": {"thumbnail": {"href": "https://example.test/preview.jpg"}},
            }
        ]
    }
    scene = parse_scene_catalog(payload)[0]
    assert scene["scene_id"] == "scene-1"
    assert scene["thumbnail_url"].endswith("preview.jpg")


def test_daily_risk_increases_for_wet_warm_rapid_change():
    quiet = DailyGlacierFeatures(1, 2, 5, 3, 0, 0.1, 0.5)
    active = DailyGlacierFeatures(20, 45, 130, 60, -0.4, 3.5, 0.8)
    assert screen_daily_risk(active).score > screen_daily_risk(quiet).score
    assert screen_daily_risk(active).band in {"elevated watch", "high watch"}


def test_missing_and_stale_data_reduce_confidence():
    fresh = DailyGlacierFeatures(5, 10, 20, 10, -0.1, 0.5, 0.5)
    stale = DailyGlacierFeatures(
        5,
        10,
        20,
        10,
        -0.1,
        0.5,
        0.5,
        missing_fraction=0.5,
        optical_age_days=21,
        sar_age_days=24,
    )
    assert screen_daily_risk(stale).confidence < screen_daily_risk(fresh).confidence
