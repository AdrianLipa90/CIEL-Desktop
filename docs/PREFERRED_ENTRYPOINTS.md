# Preferred Entrypoints

## Canonical entrypoint after merge

Use:

```bash
python scripts/run_ciel.py
```

This is the preferred desktop entrypoint because it opens the Launcher Hub and lets the operator choose between the currently available shell modes without remembering multiple scripts.

## Compatibility entrypoints

These remain useful but should be treated as direct mode launchers rather than the default entrypoint:

- `python scripts/run_ciel_desktop.py`  → minimal bootstrap shell
- `python scripts/run_ciel_native_gui.py`  → componentized shell v1
- `python scripts/run_ciel_native_gui_v2.py`  → richer shell with Metrics + Reports
- `python scripts/run_ciel_launcher_hub.py`  → direct launcher-hub call

## Merge intent

After review, the repository should expose a single obvious launch path to humans:

```bash
python scripts/run_ciel.py
```

The other scripts can remain for development, debugging, and explicit mode selection.

## Architectural intent

- keep `CIEL-_SOT_Agent` as source of truth
- keep `CIEL-Desktop` as presentation/operator layer
- keep launcher complexity low for humans
- avoid hiding multiple competing startup paths behind unclear naming
