# Documentation Index

This is the local documentation portal for the desktop-layer work on PR #2.

## Orientation

Start here if you want the shortest path to understanding the branch.

1. `PR2_DESCRIPTION.md`
   - what the branch actually contains
2. `LOCAL_INDEX.md`
   - local map of scripts, modules, docs, tests, and semantic paths
3. `GLOBAL_CONTEXT_INTRO.md`
   - how `CIEL-Desktop` sits inside the broader system

## Runtime and launch policy

- `PREFERRED_ENTRYPOINTS.md`
  - preferred vs compatibility launch paths
- `CANONICAL_NATIVE_GUI.md`
  - preferred native GUI surface and meaning of canonical mode
- `NATIVE_GUI_RUNBOOK.md`
  - how to run the shell variants and what they do

## Validation and readiness

- `PR2_TEST_CHECKLIST.md`
  - manual validation plan for the richer desktop shells
- `MERGE_READINESS.md`
  - what is strong, what is transitional, and what remains imperfect before merge

## Reading order by role

### If you are reviewing architecture

Read in this order:

- `GLOBAL_CONTEXT_INTRO.md`
- `PR2_DESCRIPTION.md`
- `CANONICAL_NATIVE_GUI.md`
- `MERGE_READINESS.md`

### If you are trying to run the software

Read in this order:

- `PREFERRED_ENTRYPOINTS.md`
- `NATIVE_GUI_RUNBOOK.md`
- `PR2_TEST_CHECKLIST.md`

### If you are mapping repository structure

Read in this order:

- `LOCAL_INDEX.md`
- `GLOBAL_CONTEXT_INTRO.md`

## Short semantic summary

- `CIEL-_SOT_Agent` remains the upstream source of truth
- `CIEL-Desktop` remains the presentation/operator layer
- `scripts/run_ciel.py` is the preferred human-facing launcher
- `native_gui_canonical` is the preferred native GUI surface on this branch
