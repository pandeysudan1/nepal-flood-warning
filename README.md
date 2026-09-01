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

The prototype assumes downstream velocity decays as v(x) = v0 exp(-kx) and integrates travel time along the corridor. Detection delay is added before warning arrival time. Evacuation margin is arrival time minus required evacuation time.

This deliberately simple model makes every assumption visible. It is suitable for concept development, stakeholder discussion, and training—not live emergency decisions.

## Roadmap

1. Calibrate travel time using gauging stations and historical flood events.
2. Estimate surface velocity from camera frames with optical flow.
3. Fuse rainfall, water level, camera, and satellite observations.
4. Add uncertainty intervals and sensor-failure handling.
5. Connect a sandbox SMS provider with human authorization.
6. Validate thresholds and governance with responsible Nepal authorities.

## Safety

This repository is a research prototype. Do not use its outputs for operational warnings or evacuation decisions without field calibration, independent validation, redundant sensing, human oversight, and authorization by responsible agencies.
