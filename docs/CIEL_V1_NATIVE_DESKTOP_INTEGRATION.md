# CIEL v1 Native Desktop Integration

This repository owns the desktop shell.

## Current implementation notes

- native Python + tkinter
- split layout: Top Status Bar + Left Rail + Main Workspace + Right Context Drawer
- local adapter to `CIEL-_SOT_Agent`
- live GitHub enrichment is optional and additive
- operator actions are executed against the local engine checkout

## Current bridge mode

The desktop repo expects a local engine checkout referenced by:

```bash
export CIEL_SOT_AGENT_ROOT=/absolute/path/to/CIEL-_SOT_Agent
```

## Current operator actions

- `run_sync`
- `run_orbital`
- `rebuild_packet`
- `operator_cycle`

## Long-term target

Move from direct local import bridging toward a thinner explicit engine contract, so the desktop shell consumes state rather than importing broad engine internals.
