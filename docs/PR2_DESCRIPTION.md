# PR #2 Expanded Description

## What this branch actually contains

This branch is no longer only a single richer shell prototype.
It now contains a structured desktop-surface exploration for `CIEL-Desktop` that keeps `CIEL-_SOT_Agent` as the canonical source of truth.

## Main additions

### Desktop shell surfaces

- bootstrap shell already present on `main`
- `native_gui_shell` as the first componentized control-home style shell
- `native_gui_shell_v2` as the richer shell with real Metrics and Reports panels
- `native_gui_canonical` as the preferred native GUI surface moving forward

### Launch surfaces

- `scripts/run_ciel.py` as the preferred human-facing launcher
- `scripts/run_ciel_launcher_hub.py` as the direct launcher-hub call
- direct compatibility launchers for bootstrap / v1 / v2 / canonical modes

### Desktop operator contract

The branch keeps the desktop application as a presentation/operator layer only.
It does not redefine orbital truth, repo-phase truth, or Sapiens packet truth.
Those remain in `CIEL-_SOT_Agent`.

### Engine coupling

The desktop layer consumes the engine through the adapter bridge and local checkout resolution.
The richer shells:

- refresh local engine-derived state
- display reduced state metrics
- allow explicit operator actions
- write action artifacts under the engine checkout

## Operator actions currently exposed

- `run_sync`
- `run_orbital`
- `rebuild_packet`
- `operator_cycle`

## Quality additions

The branch now also includes:

- a manual PR test checklist
- smoke-level import tests for desktop entrypoint modules
- explicit entrypoint policy docs
- explicit canonical-native-GUI docs

## Merge intent

After review, the repository should present:

1. one obvious human launcher
2. one obvious canonical native GUI surface
3. compatibility/dev launchers only as explicit secondary paths

## What this branch is not yet

This branch is not yet the final refactored architecture.
It still contains duplication between the earlier componentized shell and the richer v2 layer.
The current goal is to reach a reviewable, testable, semantically ordered surface before deeper consolidation.
