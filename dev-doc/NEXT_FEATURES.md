# Next Features

This document defines the proposed development path after version 0.1. The immediate priority is to replace manually entered camera observations with a reproducible camera-analysis pipeline while retaining human control over every warning.

## Next feature: camera-based surface-velocity estimation

### Goal

Allow the user to upload a short river video or select a demonstration video. The application will estimate surface-water velocity between consecutive frames and pass the result to the existing flood-routing model.

### Proposed workflow

1. Upload an MP4 video or image sequence.
2. Select a visible river region of interest.
3. Enter or detect a physical reference length for pixel-to-metre calibration.
4. Track visible surface features with optical flow.
5. Remove unreliable vectors and calculate a robust median velocity.
6. Display the tracked vectors, confidence score, and velocity time series.
7. Require the operator to review and approve the estimate.
8. Send the approved value to the existing corridor simulation.

### Initial implementation tasks

- Add OpenCV as an optional dependency.
- Create `src/nepal_flood_warning/camera.py`.
- Implement frame sampling and Farnebäck or Lucas–Kanade optical flow.
- Add pixel-to-metre and frame-time conversion.
- Add confidence and data-quality checks.
- Add a new Camera Analysis page to the Streamlit application.
- Include a small non-emergency demonstration video or synthetic fixture.
- Add tests using synthetic motion with a known velocity.

### Acceptance criteria

- The same demonstration video produces a repeatable velocity estimate.
- Synthetic test motion is estimated within a documented tolerance.
- Missing calibration prevents conversion to metres per second.
- Low-quality or contradictory measurements are clearly rejected.
- The application shows the original video, analysis region, motion vectors, estimate, and confidence.
- Camera results never trigger an SMS or evacuation alert automatically.

## Features after camera analysis

### 1. Uncertainty-aware arrival forecasts

Replace the single arrival time with a range based on uncertainty in camera velocity, attenuation, detection delay, and calibration. Show earliest, median, and latest arrival estimates.

### 2. Historical-event calibration

Add observed gauge and event data to estimate corridor-specific routing parameters instead of relying on illustrative values.

### 3. Multi-sensor fusion

Combine camera velocity with rainfall, water level, upstream gauge, and satellite observations. Each sensor should have timestamp, status, confidence, and failure handling.

### 4. River-network representation

Replace the single corridor table with a directed river graph containing tributaries, sensor sites, settlements, bridges, hydropower assets, and evacuation zones.

### 5. Scenario playback

Allow users to run historical or synthetic scenarios over time and watch the estimated flood signal move downstream on the map.

### 6. Alert-message sandbox

Generate Nepali and English warning drafts in a closed sandbox. Messages must remain in preview mode until an authorized human approves a future operational integration.

### 7. Reliability dashboard

Show sensor health, communication delay, stale data, battery state, camera visibility, missing settlements, and estimated SMS delivery failures.

## Suggested release sequence

| Release | Scope | Main outcome |
|---|---|---|
| `v0.2` | Camera analysis prototype | Video-to-velocity estimate with confidence |
| `v0.3` | Uncertainty model | Arrival-time intervals instead of single values |
| `v0.4` | Calibration pipeline | Parameters fitted to historical observations |
| `v0.5` | Multi-sensor and river graph | More realistic corridor and tributary modelling |
| `v0.6` | Scenario playback and alert sandbox | Training and stakeholder-demonstration system |

## Recommended immediate milestone

Build `v0.2` using one short demonstration video and one synthetic optical-flow test. Keep the first implementation small: a single camera, one calibrated region, one velocity estimate, and an explicit operator-approval button before the value enters the flood model.

