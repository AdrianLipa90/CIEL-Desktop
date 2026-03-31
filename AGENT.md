# AGENT.md

## Scope

This repository owns the desktop GUI and presentation-layer behavior of CIEL.

It does not become a second source of truth for orbital, repo-phase, bridge, or Sapiens logic.

## Rules

- Keep engine truth in `CIEL-_SOT_Agent`.
- Keep UI identity and presentation rules in this repo.
- Prefer thin adapters over duplicated core logic.
- Expose operator actions clearly with visible state transitions and provenance.
- Preserve epistemic separation: fact / derived / inferred / unknown.
