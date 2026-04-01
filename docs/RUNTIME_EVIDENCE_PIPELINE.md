# Desktop Runtime Evidence Pipeline

## Purpose

This document describes how `CIEL-Desktop` participates in the cross-repository runtime evidence loop with `CIEL-_SOT_Agent`.

## Flow

1. `CIEL-_SOT_Agent` declares the accepted execution modes and required evidence fields.
2. `CIEL-Desktop` runs a local runtime probe.
3. `CIEL-Desktop` writes a runtime evidence JSON artifact.
4. `CIEL-_SOT_Agent` ingests the artifact through `ciel_sot_agent.runtime_evidence_ingest`.

## Current probe

The current probe is intentionally minimal.
It measures:
- sync report build time,
- orbital bridge build time,
- panel state build time,
- total cold-start time for the probe path.

It does not yet certify:
- GUI event-loop behavior,
- audio runtime,
- STT/TTS runtime,
- GGUF local-model runtime.

## Running

```bash
python scripts/run_runtime_evidence_probe.py --sot-root /path/to/CIEL-_SOT_Agent
```

Default output:

```text
runtime_evidence/desktop_runtime_evidence.json
```

## Audit discipline

A successful probe is evidence for the specific execution path exercised by this script.
It is not a blanket certification of all desktop runtime modes.
