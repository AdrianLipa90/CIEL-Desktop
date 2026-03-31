# Local Index

This is the local index for the desktop-layer work currently present on PR #2.

## Root intent

`CIEL-Desktop` owns the desktop GUI and operator-facing presentation layer.
It does not become a second engine.

## Scripts

### Preferred launcher

- `scripts/run_ciel.py`
  - preferred human-facing launch path
  - opens the Launcher Hub

### Direct launcher hub

- `scripts/run_ciel_launcher_hub.py`
  - direct access to the launcher hub

### Direct shell launchers

- `scripts/run_ciel_desktop.py`
  - minimal bootstrap shell
- `scripts/run_ciel_native_gui.py`
  - componentized native GUI v1
- `scripts/run_ciel_native_gui_v2.py`
  - richer native GUI with Metrics and Reports
- `scripts/run_ciel_native_gui_canonical.py`
  - preferred native GUI surface

## Source modules

### Core package root

- `src/ciel_desktop/__init__.py`
- `src/ciel_desktop/config.py`
- `src/ciel_desktop/main.py`

### Adapter / engine bridge

- `src/ciel_desktop/core/sot_adapter.py`
  - resolves the local `CIEL-_SOT_Agent` checkout
  - imports engine functions from the canonical repo

- `src/ciel_desktop/core/operator_actions.py`
  - runs explicit operator actions against the engine
  - writes action artifacts under the engine checkout

### Launcher layer

- `src/ciel_desktop/launcher_hub.py`
  - unified launcher chooser for shell modes

### Native GUI surfaces

- `src/ciel_desktop/native_gui_shell.py`
  - first componentized control-home style shell

- `src/ciel_desktop/native_gui_shell_v2.py`
  - richer shell with real Metrics and Reports panels

- `src/ciel_desktop/native_gui_canonical.py`
  - preferred native GUI module moving forward

## Documentation

- `docs/PR2_DESCRIPTION.md`
  - expanded semantic description of PR #2 scope
- `docs/PREFERRED_ENTRYPOINTS.md`
  - preferred vs compatibility launch paths
- `docs/CANONICAL_NATIVE_GUI.md`
  - intent and meaning of canonical native GUI surface
- `docs/NATIVE_GUI_RUNBOOK.md`
  - runtime instructions and shell-mode usage
- `docs/PR2_TEST_CHECKLIST.md`
  - manual validation checklist for review
- `docs/LOCAL_INDEX.md`
  - this file
- `docs/GLOBAL_CONTEXT_INTRO.md`
  - relation to the broader system landscape

## Tests

- `tests/test_desktop_entrypoints.py`
  - smoke-level module import checks
  - checks `main()` presence for desktop entrypoints

## Local semantic map

### Human launch surface

`run_ciel.py` -> `launcher_hub` -> chosen shell mode

### Native GUI path

`native_gui_canonical` -> currently backed by `native_gui_shell_v2`

### Truth path

`CIEL-Desktop` -> `sot_adapter` -> local `CIEL-_SOT_Agent` checkout -> canonical engine state

### Explicit write path

Desktop operator action -> `operator_actions.py` -> engine artifact under `integration/reports/native_gui_actions/`
