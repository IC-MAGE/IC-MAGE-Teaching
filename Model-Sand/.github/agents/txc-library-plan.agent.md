---
name: txc-library-plan
description: "Use when planning or implementing the OOP refactor of the standalone TXC M02/M09 script into a reusable Python library. Covers package structure, core classes, numerical safeguards, plotting, export, and regression checks against the original script."
---

Refactor the standalone TXC integrator script into a new installable Python package under `m02_tx_integrator/` using a `src/` layout. Do not modify the original script.

Focus the implementation on a TXC-only library with one combined integrator class for the existing M02+M09 behaviour. Separate responsibilities into:
- parameter dataclasses for material and small-strain stiffness inputs
- test-condition dataclass for `label`, `e0`, `p0`, `q0`
- result container with DataFrame conversion
- core integrator class with single-test and batch execution
- plotting helpers
- CSV export helpers

Recommended structure:
- `m02_tx_integrator/pyproject.toml`
- `m02_tx_integrator/src/m02_tx_integrator/__init__.py`
- `m02_tx_integrator/src/m02_tx_integrator/parameters.py`
- `m02_tx_integrator/src/m02_tx_integrator/presets.py`
- `m02_tx_integrator/src/m02_tx_integrator/test_conditions.py`
- `m02_tx_integrator/src/m02_tx_integrator/results.py`
- `m02_tx_integrator/src/m02_tx_integrator/integrator.py`
- `m02_tx_integrator/src/m02_tx_integrator/plotter.py`
- `m02_tx_integrator/src/m02_tx_integrator/exporter.py`

Implementation expectations:
- Preserve numerical behaviour of the original script by default.
- Keep default elastic/plastic step counts aligned with the script.
- Replace fixed top-of-file constants with constructor inputs, presets, and per-test inputs.
- Provide Nevada sand presets matching the current `set == 1` and `set == 2` branches.
- Support batch execution across multiple tests.
- Include plotting helpers for stress path, stress-strain, and volumetric response.
- Include CSV export compatible with the current workflow.

Critical review points to apply during implementation:
- The peak-condition iteration currently uses a hard-coded 100-step fixed-point loop with no convergence test; add a tolerance and explicit failure path.
- Configurable step counts improve flexibility but can silently change validated outputs; document and preserve defaults.
- Decide whether DataFrame/CSV output should exactly preserve legacy duplicate columns for downstream compatibility or provide a clean schema with an optional compatibility mode.
- Avoid making plotting a mandatory runtime dependency if possible; prefer optional import or extras.
- Keep internal phase logic testable by separating peak-state calculation, elastic integration, and plastic integration.

Verification requirements:
- Install the package locally and confirm imports succeed.
- Reproduce at least one original test case and compare output numerically against the standalone script.
- Run the original batch of tests through the new API.
- Confirm plotting helpers execute without error.