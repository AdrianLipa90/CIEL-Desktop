# PR #2 Manual Test Checklist

This checklist is for the draft PR that adds the richer desktop shell variants.

## Preconditions

- local checkout of `AdrianLipa90/CIEL-_SOT_Agent`
- `CIEL_SOT_AGENT_ROOT` set when the engine is not adjacent to `CIEL-Desktop`
- Python environment with tkinter available

## 1. Bootstrap shell

```bash
python scripts/run_ciel_desktop.py
```

Check:

- app window opens
- status line resolves the engine path
- refresh works
- `run_sync`, `run_orbital`, `rebuild_packet`, `operator_cycle` execute without crash

## 2. Launcher Hub

```bash
python scripts/run_ciel.py
```

Check:

- launcher hub opens
- all listed modes are visible
- each launch button opens the intended shell

## 3. Native GUI v1

```bash
python scripts/run_ciel_native_gui.py
```

Check:

- TopBar updates after refresh
- StateStrip shows coherence / defect / energy / tension
- SystemMap renders central state and nodes
- ActionSurface buttons execute actions and append log rows
- FocusObject updates after refresh
- TemporalLayer shows timeline rows

## 4. Native GUI canonical

```bash
python scripts/run_ciel_native_gui_canonical.py
```

Check:

- canonical window title is visible
- Metrics panel is reachable from navigation
- Reports panel is reachable from navigation

## 5. Native GUI v2

```bash
python scripts/run_ciel_native_gui_v2.py
```

Check:

- Metrics panel shows pairwise tensions when available
- Reports panel lists report files
- selecting a report shows preview content

## 6. Engine artifacts

After running operator actions, verify files appear under:

```text
integration/reports/native_gui_actions/
```

## 7. Regression expectation

- `CIEL-_SOT_Agent` remains the source of truth
- `CIEL-Desktop` remains presentation/operator layer only
- no shell mode should silently mutate engine logic outside explicit operator actions
