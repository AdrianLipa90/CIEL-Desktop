# Native GUI Runbook

## Local engine dependency

`CIEL-Desktop` currently expects a local checkout of `AdrianLipa90/CIEL-_SOT_Agent`.

Set the path explicitly when needed:

```bash
export CIEL_SOT_AGENT_ROOT=/absolute/path/to/CIEL-_SOT_Agent
```

If `CIEL-_SOT_Agent` sits next to this repo, the adapter will usually resolve it automatically.

## Entry points

### 1. Stable bootstrap shell

```bash
python scripts/run_ciel_desktop.py
```

Use this when you want the simpler desktop bootstrap already present on `main`.

### 2. Componentized native shell v1

```bash
python scripts/run_ciel_native_gui.py
```

This launches the richer control-home style shell introduced in PR #2.

### 3. Native shell v2 with real Metrics and Reports panels

```bash
python scripts/run_ciel_native_gui_v2.py
```

This launches the richer variant that adds:

- a populated Metrics panel
- a populated Reports panel with file preview
- the same local operator action bridge into `CIEL-_SOT_Agent`

## Operator actions

The richer shells expose:

- `run_sync`
- `run_orbital`
- `rebuild_packet`
- `operator_cycle`

These actions write artifacts under the engine checkout in:

```text
integration/reports/native_gui_actions/
```

## Notes

The richer shells currently treat `CIEL-_SOT_Agent` as the source of truth and consume it through the desktop adapter layer.
They do not replace engine logic.
