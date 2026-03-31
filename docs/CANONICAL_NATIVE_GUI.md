# Canonical Native GUI

## Intent

This branch now defines a canonical native GUI surface:

```bash
python scripts/run_ciel_native_gui_canonical.py
```

The canonical module currently reuses the richer v2 shell because v2 already contains the real Metrics and Reports panels.

## Why this exists

The branch accumulated multiple native shell entrypoints while the GUI architecture was still being explored.
That is normal during prototyping, but it becomes noisy for humans.

This document sets the intended interpretation:

- `native_gui_canonical` = preferred native GUI surface
- `native_gui_shell_v2` = richer implementation currently backing the canonical surface
- `native_gui_shell` = earlier componentized shell kept for compatibility/dev reference

## Human-facing launch paths

### Preferred native GUI surface

```bash
python scripts/run_ciel_native_gui_canonical.py
```

### Unified launcher hub

```bash
python scripts/run_ciel.py
```

This remains the easiest general-purpose launch path for humans because it exposes all currently available shell modes from one place.

## Merge intent

After review, the repository should keep:

- one clear general launcher (`scripts/run_ciel.py`)
- one clear canonical native GUI module (`native_gui_canonical`)
- older shell-specific scripts only as explicit compatibility/dev entrypoints
