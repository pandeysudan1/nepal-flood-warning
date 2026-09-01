"""Transparent first-order flood routing and warning logic.

This is a planning and training model, not an operational forecasting system.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import exp

import pandas as pd


class AlertLevel(StrEnum):
    NORMAL = "Normal"
    WATCH = "Watch"
    WARNING = "Warning"
    EVACUATE = "Evacuate"


@dataclass(frozen=True)
class SimulationConfig:
    camera_velocity_mps: float = 5.0
    camera_rise_rate_mph: float = 0.8
    evacuation_time_min: float = 25.0
    detection_delay_min: float = 2.0
    routing_attenuation_per_km: float = 0.006
    sms_delivery_rate: float = 0.92

    def validate(self) -> None:
        if self.camera_velocity_mps <= 0:
            raise ValueError("camera_velocity_mps must be positive")
        if self.evacuation_time_min < 0 or self.detection_delay_min < 0:
            raise ValueError("time inputs cannot be negative")
        if self.routing_attenuation_per_km < 0:
            raise ValueError("attenuation cannot be negative")
        if not 0 <= self.sms_delivery_rate <= 1:
            raise ValueError("sms_delivery_rate must be between 0 and 1")


def _travel_minutes(distance_km: float, velocity_mps: float, attenuation: float) -> float:
    """Integrate travel time where velocity decays exponentially downstream."""
    if distance_km <= 0:
        return 0.0
    if attenuation == 0:
        return distance_km * 1000 / velocity_mps / 60
    seconds = 1000 * (exp(attenuation * distance_km) - 1) / (velocity_mps * attenuation)
    return seconds / 60


def _alert_level(rise_rate: float, velocity: float, margin_min: float) -> AlertLevel:
    if margin_min < 0 or rise_rate >= 1.2 or velocity >= 6.0:
        return AlertLevel.EVACUATE
    if margin_min < 15 or rise_rate >= 0.7 or velocity >= 4.0:
        return AlertLevel.WARNING
    if margin_min < 30 or rise_rate >= 0.3 or velocity >= 2.0:
        return AlertLevel.WATCH
    return AlertLevel.NORMAL


def simulate_corridor(sites: pd.DataFrame, config: SimulationConfig) -> pd.DataFrame:
    """Calculate flood arrival, evacuation margin, and SMS reach for each site."""
    config.validate()
    required = {"site", "distance_km", "population", "latitude", "longitude"}
    missing = required.difference(sites.columns)
    if missing:
        raise ValueError(f"missing columns: {', '.join(sorted(missing))}")
    if (sites["distance_km"] < 0).any() or (sites["population"] < 0).any():
        raise ValueError("distance and population cannot be negative")

    result = sites.copy()
    travel = result["distance_km"].map(
        lambda d: _travel_minutes(
            float(d), config.camera_velocity_mps, config.routing_attenuation_per_km
        )
    )
    result["arrival_min"] = travel + config.detection_delay_min
    result["evacuation_margin_min"] = result["arrival_min"] - config.evacuation_time_min
    result["routed_velocity_mps"] = config.camera_velocity_mps * (
        (-config.routing_attenuation_per_km * result["distance_km"]).map(exp)
    )
    result["alert_level"] = result.apply(
        lambda row: _alert_level(
            config.camera_rise_rate_mph,
            float(row["routed_velocity_mps"]),
            float(row["evacuation_margin_min"]),
        ).value,
        axis=1,
    )
    result["sms_reached"] = (result["population"] * config.sms_delivery_rate).round().astype(int)
    result["people_not_reached"] = result["population"] - result["sms_reached"]
    return result

