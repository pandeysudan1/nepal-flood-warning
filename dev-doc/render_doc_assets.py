"""Render mobile-safe PNG diagrams and equations for the development notes."""

from __future__ import annotations

from pathlib import Path
from textwrap import wrap

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ASSET_DIR = Path(__file__).with_name("assets")
GREEN = "#1f7a5c"
GREEN_LIGHT = "#e7f4ef"
BLUE = "#2457a7"
TEXT = "#17212b"
LINE = "#52616b"


def render_flow(name: str, layers: list[list[str]], edges: list[tuple[str, str]]) -> None:
    """Render a layered box-and-arrow flowchart."""
    width = 9.0
    height = max(3.0, 1.45 * len(layers) + 0.5)
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    positions: dict[str, tuple[float, float]] = {}
    box_w = 0.34 if any(len(layer) > 1 for layer in layers) else 0.54
    box_h = min(0.13, 0.62 / len(layers))

    for row, layer in enumerate(layers):
        y = 0.91 - row * (0.82 / max(1, len(layers) - 1))
        xs = [0.5] if len(layer) == 1 else [0.27, 0.73]
        for label, x in zip(layer, xs, strict=True):
            positions[label] = (x, y)

    for source, target in edges:
        x1, y1 = positions[source]
        x2, y2 = positions[target]
        arrow = FancyArrowPatch(
            (x1, y1 - box_h / 2),
            (x2, y2 + box_h / 2),
            arrowstyle="-|>",
            mutation_scale=18,
            linewidth=1.8,
            color=LINE,
            connectionstyle="arc3,rad=0.0",
            zorder=1,
        )
        ax.add_patch(arrow)

    for label, (x, y) in positions.items():
        box = FancyBboxPatch(
            (x - box_w / 2, y - box_h / 2),
            box_w,
            box_h,
            boxstyle="round,pad=0.014,rounding_size=0.018",
            linewidth=2,
            edgecolor=GREEN,
            facecolor=GREEN_LIGHT,
            zorder=2,
        )
        ax.add_patch(box)
        shown = "\n".join(wrap(label, width=25))
        ax.text(x, y, shown, ha="center", va="center", fontsize=12.5, color=TEXT, zorder=3)

    fig.savefig(
        ASSET_DIR / f"{name}.png",
        format="png",
        dpi=180,
        bbox_inches="tight",
        pad_inches=0.08,
        facecolor="white",
    )
    plt.close(fig)


def render_equation(name: str, expression: str, width: float = 9.0) -> None:
    """Render a MathText expression as an SVG image."""
    fig = plt.figure(figsize=(width, 1.25))
    fig.patch.set_facecolor("white")
    fig.text(0.5, 0.5, f"${expression}$", ha="center", va="center", fontsize=25, color=TEXT)
    fig.savefig(
        ASSET_DIR / f"{name}.png",
        format="png",
        dpi=180,
        bbox_inches="tight",
        pad_inches=0.16,
        facecolor="white",
    )
    plt.close(fig)


def main() -> None:
    ASSET_DIR.mkdir(exist_ok=True)

    flows = {
        "v01-workflow": (
            [["Camera observation"], ["Operator inputs"], ["Flood routing"], ["Arrival time"], ["Alert level"]],
            [("Camera observation", "Operator inputs"), ("Operator inputs", "Flood routing"), ("Flood routing", "Arrival time"), ("Arrival time", "Alert level")],
        ),
        "sms-coverage": (
            [["Site population", "Delivery rate"], ["SMS coverage"], ["Reached", "Not reached"]],
            [("Site population", "SMS coverage"), ("Delivery rate", "SMS coverage"), ("SMS coverage", "Reached"), ("SMS coverage", "Not reached")],
        ),
        "software-structure": (
            [["Streamlit dashboard", "Corridor CSV"], ["Simulation model"], ["Map and charts", "Pytest suite"]],
            [("Streamlit dashboard", "Simulation model"), ("Corridor CSV", "Simulation model"), ("Simulation model", "Map and charts"), ("Simulation model", "Pytest suite")],
        ),
        "downstream-velocity": (
            [["Observed velocity v₀", "Distance x and coefficient k"], ["Exponential attenuation"], ["Routed velocity v(x)"]],
            [("Observed velocity v₀", "Exponential attenuation"), ("Distance x and coefficient k", "Exponential attenuation"), ("Exponential attenuation", "Routed velocity v(x)")],
        ),
        "travel-time": (
            [["Routed velocity", "Detection delay"], ["Travel-time integral"], ["Arrival time"]],
            [("Routed velocity", "Travel-time integral"), ("Travel-time integral", "Arrival time"), ("Detection delay", "Arrival time")],
        ),
        "alert-logic": (
            [["Arrival time", "Required time"], ["Evacuation margin"], ["Margin, velocity, and rise rate"], ["Threshold rules"], ["Alert state"]],
            [("Arrival time", "Evacuation margin"), ("Required time", "Evacuation margin"), ("Evacuation margin", "Margin, velocity, and rise rate"), ("Margin, velocity, and rise rate", "Threshold rules"), ("Threshold rules", "Alert state")],
        ),
        "build-record": (
            [["Create package"], ["Add model and data"], ["Test and lint"], ["Commit locally"], ["Publish on GitHub"]],
            [("Create package", "Add model and data"), ("Add model and data", "Test and lint"), ("Test and lint", "Commit locally"), ("Commit locally", "Publish on GitHub")],
        ),
        "operational-boundary": (
            [["Research prototype"], ["Calibration", "Field validation"], ["Redundant sensing"], ["Operational review"]],
            [("Research prototype", "Calibration"), ("Research prototype", "Field validation"), ("Calibration", "Redundant sensing"), ("Field validation", "Redundant sensing"), ("Redundant sensing", "Operational review")],
        ),
        "v02-objective": (
            [["River video"], ["Motion estimate"], ["Quality check"], ["Operator review"], ["Flood model"]],
            [("River video", "Motion estimate"), ("Motion estimate", "Quality check"), ("Quality check", "Operator review"), ("Operator review", "Flood model")],
        ),
        "measurement-workflow": (
            [["Upload video"], ["Select river region"], ["Set distance scale"], ["Track surface motion"], ["Filter and summarize"], ["Review result"], ["Approve or reject"]],
            [("Upload video", "Select river region"), ("Select river region", "Set distance scale"), ("Set distance scale", "Track surface motion"), ("Track surface motion", "Filter and summarize"), ("Filter and summarize", "Review result"), ("Review result", "Approve or reject")],
        ),
        "velocity-calculation": (
            [["Pixel displacement", "Scale and frame time"], ["Velocity conversion"], ["Median estimate"], ["Relative spread"]],
            [("Pixel displacement", "Velocity conversion"), ("Scale and frame time", "Velocity conversion"), ("Velocity conversion", "Median estimate"), ("Median estimate", "Relative spread")],
        ),
        "code-changes": (
            [["Camera page"], ["camera.py"], ["OpenCV optical flow", "Quality metrics"], ["Existing flood model"]],
            [("Camera page", "camera.py"), ("camera.py", "OpenCV optical flow"), ("camera.py", "Quality metrics"), ("camera.py", "Existing flood model")],
        ),
        "acceptance-tests": (
            [["Video loaded?"], ["Calibration valid?", "Reject: no video"], ["Motion quality adequate?", "Reject: no calibration"], ["Show result for approval", "Reject: poor motion"]],
            [("Video loaded?", "Calibration valid?"), ("Video loaded?", "Reject: no video"), ("Calibration valid?", "Motion quality adequate?"), ("Calibration valid?", "Reject: no calibration"), ("Motion quality adequate?", "Show result for approval"), ("Motion quality adequate?", "Reject: poor motion")],
        ),
        "v03-uncertainty": (
            [["Input distributions"], ["Routing ensemble"], ["Arrival interval"], ["Decision display"]],
            [("Input distributions", "Routing ensemble"), ("Routing ensemble", "Arrival interval"), ("Arrival interval", "Decision display")],
        ),
        "v04-calibration": (
            [["Historical events"], ["Parameter fitting"], ["Validation events"], ["Corridor parameters"]],
            [("Historical events", "Parameter fitting"), ("Parameter fitting", "Validation events"), ("Validation events", "Corridor parameters")],
        ),
        "v05-sensor-fusion": (
            [["Camera, gauge, and rainfall", "Satellite input"], ["Sensor fusion"], ["River graph"], ["Asset and settlement risk"]],
            [("Camera, gauge, and rainfall", "Sensor fusion"), ("Satellite input", "Sensor fusion"), ("Sensor fusion", "River graph"), ("River graph", "Asset and settlement risk")],
        ),
        "v06-playback": (
            [["Event scenario"], ["Time playback"], ["Map and warnings"], ["Message preview"], ["Operator decision"]],
            [("Event scenario", "Time playback"), ("Time playback", "Map and warnings"), ("Map and warnings", "Message preview"), ("Message preview", "Operator decision")],
        ),
        "release-sequence": (
            [["v0.2 Camera measurement"], ["v0.3 Uncertainty"], ["v0.4 Calibration"], ["v0.5 Sensor network"], ["v0.6 Training sandbox"]],
            [("v0.2 Camera measurement", "v0.3 Uncertainty"), ("v0.3 Uncertainty", "v0.4 Calibration"), ("v0.4 Calibration", "v0.5 Sensor network"), ("v0.5 Sensor network", "v0.6 Training sandbox")],
        ),
        "immediate-milestone": (
            [["One video"], ["One calibrated region"], ["One velocity estimate"], ["One quality result"], ["Approve or reject"]],
            [("One video", "One calibrated region"), ("One calibrated region", "One velocity estimate"), ("One velocity estimate", "One quality result"), ("One quality result", "Approve or reject")],
        ),
        "satellite-architecture": (
            [["Daily MODIS, GPM, and ERA5", "Sentinel-1 and Sentinel-2 snapshots"], ["Daily feature table"], ["Watch index and confidence"], ["Human review"]],
            [("Daily MODIS, GPM, and ERA5", "Daily feature table"), ("Sentinel-1 and Sentinel-2 snapshots", "Daily feature table"), ("Daily feature table", "Watch index and confidence"), ("Watch index and confidence", "Human review")],
        ),
        "daily-feature-flow": (
            [["Scene catalogue", "Weather data"], ["Quality masks and feature extraction"], ["One row per lake per day"]],
            [("Scene catalogue", "Quality masks and feature extraction"), ("Weather data", "Quality masks and feature extraction"), ("Quality masks and feature extraction", "One row per lake per day")],
        ),
        "glof-development-phases": (
            [["Inventory and polygons"], ["Historical feature archive"], ["Event and non-event labels"], ["Calibrated model"], ["Shadow-mode validation"], ["Operational decision review"]],
            [("Inventory and polygons", "Historical feature archive"), ("Historical feature archive", "Event and non-event labels"), ("Event and non-event labels", "Calibrated model"), ("Calibrated model", "Shadow-mode validation"), ("Shadow-mode validation", "Operational decision review")],
        ),
    }

    for name, (layers, edges) in flows.items():
        render_flow(name, layers, edges)

    equations = {
        "eq-downstream-velocity": r"v(x)=v_0\exp(-kx)",
        "eq-travel-positive": r"t_{\mathrm{travel}}(x)=\frac{1000}{v_0k}\left[\exp(kx)-1\right],\quad k>0",
        "eq-travel-zero": r"t_{\mathrm{travel}}(x)=\frac{1000x}{v_0},\quad k=0",
        "eq-arrival-time": r"t_{\mathrm{arrival}}(x)=\frac{t_{\mathrm{travel}}(x)}{60}+t_{\mathrm{delay}}",
        "eq-evacuation-margin": r"M_{\mathrm{evac}}(x)=t_{\mathrm{arrival}}(x)-t_{\mathrm{required}}",
        "eq-sms-reached": r"N_{\mathrm{reached}}=\operatorname{round}\!\left(Np_{\mathrm{SMS}}\right)",
        "eq-sms-unreached": r"N_{\mathrm{unreached}}=N-N_{\mathrm{reached}}",
        "eq-video-velocity": r"\hat{v}=\frac{s\,\Delta p}{\Delta t}",
        "eq-median-velocity": r"\hat{v}_{\mathrm{surface}}=\operatorname{median}\!\left(\hat{v}_1,\hat{v}_2,\ldots,\hat{v}_n\right)",
        "eq-relative-spread": r"u_{\mathrm{rel}}=\frac{1.4826\,\operatorname{median}\!\left(\left|\hat{v}_i-\hat{v}_{\mathrm{surface}}\right|\right)}{\hat{v}_{\mathrm{surface}}}",
    }
    for name, expression in equations.items():
        render_equation(name, expression)


if __name__ == "__main__":
    main()
