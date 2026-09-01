# Project Build Log

## Project

**Nepal Flood Early-Warning Simulator**  
Repository: <https://github.com/pandeysudan1/nepal-flood-warning>

## What we built

We created the first working version of a camera-assisted flash-flood warning simulator for Nepal's mountain river corridors. The demonstration case follows the Trishuli corridor from Rasuwagadhi toward Bidur.

The application accepts an observed water velocity and water-level rise rate. It routes a simplified flood signal downstream, estimates the arrival time at each settlement, compares the available warning time with the required evacuation time, and assigns an alert level.

The dashboard also estimates how many people receive an SMS warning and how many may remain unreached.

## Main components

- `app/dashboard.py` — interactive Streamlit dashboard and map.
- `src/nepal_flood_warning/model.py` — routing, evacuation-margin, alert, and SMS logic.
- `data/trishuli_corridor.csv` — demonstration settlements, locations, and population data.
- `tests/test_model.py` — automated tests for the model.
- `pyproject.toml` — Python package configuration and dependencies.
- `README.md` — installation, model explanation, safety limits, and roadmap.

## Model used in version 0.1

The prototype assumes the flood-wave velocity decreases exponentially with downstream distance:

$$
v(x)=v_0e^{-kx}
$$

The corresponding travel time is calculated as:

$$
t(x)=\frac{1000}{v_0k}\left(e^{kx}-1\right)
$$

where:

- $x$ is downstream distance in kilometres;
- $v_0$ is the camera-estimated velocity in metres per second;
- $k$ is an illustrative routing-attenuation coefficient per kilometre.

Detection delay is added to the travel time. The evacuation margin is then:

$$
M_{evac}=t_{arrival}-t_{required}
$$

The app combines this margin with water velocity and water-level rise rate to classify each location as **Normal**, **Watch**, **Warning**, or **Evacuate**.

## Development and publication record

1. Created the Python package and Streamlit application.
2. Added the Trishuli corridor demonstration dataset.
3. Added four automated model tests.
4. Ran the test suite successfully: **4 tests passed**.
5. Ran Ruff successfully: **all lint checks passed**.
6. Added a README, `.gitignore`, and MIT licence.
7. Created the public GitHub repository under `pandeysudan1`.
8. Uploaded and verified the complete project structure on GitHub.

## Important limitation

This version is a research and demonstration prototype. It must not issue real emergency warnings. Operational use requires calibrated hydrology, verified field data, redundant sensors, uncertainty analysis, reliable communications, human authorization, and formal coordination with the responsible Nepal authorities.

