import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nepal_flood_warning.model import SimulationConfig, simulate_corridor

st.set_page_config(page_title="Nepal Flood Warning", page_icon="🌊", layout="wide")
st.title("Nepal Flood Early-Warning Simulator")
st.caption("Camera observation → flood routing → evacuation margin → SMS warning")

with st.sidebar:
    st.header("Camera and response inputs")
    velocity = st.slider("Observed water velocity (m/s)", 0.5, 10.0, 5.0, 0.1)
    rise_rate = st.slider("Observed water-level rise (m/hour)", 0.0, 2.5, 0.8, 0.1)
    evacuation = st.slider("Required evacuation time (minutes)", 5, 60, 25)
    delay = st.slider("Detection and processing delay (minutes)", 0, 15, 2)
    sms_rate = st.slider("Estimated SMS delivery (%)", 50, 100, 92) / 100

sites = pd.read_csv(ROOT / "data" / "trishuli_corridor.csv")
config = SimulationConfig(
    camera_velocity_mps=velocity,
    camera_rise_rate_mph=rise_rate,
    evacuation_time_min=evacuation,
    detection_delay_min=delay,
    sms_delivery_rate=sms_rate,
)
result = simulate_corridor(sites, config)

danger = result[result["alert_level"].isin(["Warning", "Evacuate"])]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Camera velocity", f"{velocity:.1f} m/s")
c2.metric("Sites at high risk", f"{len(danger)}/{len(result)}")
c3.metric("People in high-risk sites", f"{danger['population'].sum():,.0f}")
c4.metric("SMS estimated delivered", f"{result['sms_reached'].sum():,.0f}")

colors = {"Normal": "#2a9d8f", "Watch": "#e9c46a", "Warning": "#f4a261", "Evacuate": "#e63946"}
left, right = st.columns([1.15, 1])
with left:
    st.subheader("Corridor warning map")
    fig_map = px.scatter_map(
        result,
        lat="latitude",
        lon="longitude",
        color="alert_level",
        size="population",
        hover_name="site",
        hover_data={"arrival_min": ":.1f", "evacuation_margin_min": ":.1f"},
        color_discrete_map=colors,
        zoom=8,
        height=480,
    )
    fig_map.update_layout(map_style="open-street-map", margin={"l": 0, "r": 0, "t": 0, "b": 0})
    st.plotly_chart(fig_map, use_container_width=True)

with right:
    st.subheader("Arrival and evacuation time")
    timeline = result.melt(
        id_vars="site",
        value_vars=["arrival_min", "evacuation_margin_min"],
        var_name="measure",
        value_name="minutes",
    )
    fig_time = px.bar(timeline, x="site", y="minutes", color="measure", barmode="group", height=480)
    fig_time.update_layout(xaxis_title=None, yaxis_title="Minutes", legend_title=None)
    st.plotly_chart(fig_time, use_container_width=True)

st.subheader("Operational warning table")
display = result[[
    "site", "alert_level", "arrival_min", "evacuation_margin_min",
    "routed_velocity_mps", "population", "sms_reached", "people_not_reached",
]].copy()
display.columns = [
    "Site", "Alert", "Arrival (min)", "Margin (min)", "Velocity (m/s)",
    "Population", "SMS reached", "Not reached",
]
st.dataframe(display.style.format({"Arrival (min)": "{:.1f}", "Margin (min)": "{:.1f}", "Velocity (m/s)": "{:.2f}"}), use_container_width=True, hide_index=True)

st.warning(
    "Demonstration only. Operational deployment requires calibrated hydrology, redundant sensors, "
    "field validation, official warning thresholds, and integration with Nepal's responsible authorities."
)
