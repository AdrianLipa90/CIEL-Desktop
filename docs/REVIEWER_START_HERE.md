# Reviewer Start Here

This branch has grown beyond a single GUI experiment.
If you open the PR and start reading from random files, you will understand fragments but miss the structure.

Use this order instead.

## Fast path

1. `docs/INDEX.md`
2. `docs/PR2_DESCRIPTION.md`
3. `docs/LOCAL_INDEX.md`
4. `docs/GLOBAL_CONTEXT_INTRO.md`
5. `docs/MERGE_READINESS.md`

## If you care about the formal protocol layer

Continue with:

6. `docs/specs/INDEX.md`
7. `docs/specs/CIEL0_KNOWLEDGE_COHERENCE_PROTOCOL_v0_1.md`

## If you care about running the code

Then read:

8. `docs/PREFERRED_ENTRYPOINTS.md`
9. `docs/NATIVE_GUI_RUNBOOK.md`
10. `docs/PR2_TEST_CHECKLIST.md`

## Minimal mental model

- `CIEL-_SOT_Agent` remains the canonical source of truth
- `CIEL-Desktop` remains the operator/presentation layer
- `scripts/run_ciel.py` is the preferred human-facing launcher
- `native_gui_canonical` is the preferred native GUI surface on this branch
- the richer shell is already reviewable, but internal consolidation is not yet perfect
