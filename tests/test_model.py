import pandas as pd
import pytest

from nepal_flood_warning.model import SimulationConfig, simulate_corridor


@pytest.fixture
def sites():
    return pd.DataFrame(
        {
            "site": ["Camera", "Village"],
            "distance_km": [0, 30],
            "population": [100, 1000],
            "latitude": [28.0, 27.9],
            "longitude": [85.3, 85.2],
        }
    )


def test_arrival_increases_downstream(sites):
    result = simulate_corridor(sites, SimulationConfig())
    assert result.loc[1, "arrival_min"] > result.loc[0, "arrival_min"]


def test_sms_coverage_is_calculated(sites):
    result = simulate_corridor(sites, SimulationConfig(sms_delivery_rate=0.9))
    assert result["sms_reached"].tolist() == [90, 900]
    assert result["people_not_reached"].tolist() == [10, 100]


def test_invalid_velocity_is_rejected(sites):
    with pytest.raises(ValueError, match="positive"):
        simulate_corridor(sites, SimulationConfig(camera_velocity_mps=0))


def test_faster_flow_reduces_arrival_time(sites):
    slow = simulate_corridor(sites, SimulationConfig(camera_velocity_mps=2))
    fast = simulate_corridor(sites, SimulationConfig(camera_velocity_mps=7))
    assert fast.loc[1, "arrival_min"] < slow.loc[1, "arrival_min"]

