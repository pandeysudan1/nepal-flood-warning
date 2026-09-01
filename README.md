# Nepal Flood Early-Warning Simulator

A transparent Python prototype for exploring how an upstream camera observation could support flash-flood warnings along Nepal's mountain river corridors. The first case study follows the Rasuwagadhi–Bidur section of the Trishuli corridor.

## What it does

- accepts observed flood velocity and water-level rise rate;
- routes a simplified flood signal downstream;
- estimates arrival time and evacuation margin by settlement;
- assigns Normal, Watch, Warning, or Evacuate status;
- estimates people reached and not reached by SMS;
- shows the results on an interactive map and operational table.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
streamlit run app/dashboard.py
```

Run the tests:

```bash
pytest
```

## Model

The prototype assumes downstream velocity decays as

$$v(x)=v_0 e^{-kx}$$

and integrates travel time along the corridor:

$$t(x)=\frac{1000}{v_0 k}\left(e^{kx}-1\right).$$

Here, $x$ is distance in kilometres, $v_0$ is camera-estimated velocity in m/s, and $k$ is an illustrative routing attenuation coefficient per kilometre. Detection delay is added before warning arrival time. Evacuation margin is arrival time minus required evacuation time.

This deliberately simple model makes every assumption visible. It is suitable for concept development, stakeholder discussion, and training—not live emergency decisions.

## Project structure

```text
app/dashboard.py                 Streamlit dashboard
data/trishuli_corridor.csv       Demonstration settlement data
src/nepal_flood_warning/model.py Routing and warning logic
tests/test_model.py              Unit tests
```

## Roadmap

1. Calibrate travel time using gauging stations and historical flood events.
2. Estimate surface velocity from camera frames with optical flow.
3. Fuse rainfall, water level, camera, and satellite observations.
4. Add uncertainty intervals and sensor-failure handling.
5. Connect a sandbox SMS provider and require human authorization before alerts.
6. Validate thresholds and governance with responsible Nepal authorities.

The next project phase is documented in the [satellite glacier-lake monitoring and GLOF prediction plan](dev-doc/SATELLITE_GLOF_PLAN.md). It includes official data sources, an example Sentinel-2 scene, a daily feature schema, a scene-finder script, and a staged validation plan.

## Safety

This repository is a research prototype. Do not use its outputs for operational warnings or evacuation decisions without field calibration, independent validation, redundant sensing, human oversight, and authorization by responsible agencies.
