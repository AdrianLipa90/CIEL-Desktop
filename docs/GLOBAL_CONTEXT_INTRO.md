# Introduction to Global Context

## Why this document exists

`CIEL-Desktop` can be misunderstood if read in isolation.
On its own, it may look like a standalone application project.
That would be the wrong interpretation.

This repository is only one layer in a larger system landscape.

## Global role

`CIEL-Desktop` is the operator-facing desktop surface.
It exists to render, organize, and operate on state that is produced elsewhere.

Its role is:

- presentation
- inspection
- navigation
- explicit operator triggering
- controlled state visualization

Its role is not:

- replacing the engine
- redefining orbital truth
- becoming a second source of truth for repo-phase logic
- silently inventing system state

## Canonical source of truth

The canonical source of truth remains `CIEL-_SOT_Agent`.
That repository owns the computational and integration side of the system:

- orbital computations
- repo phase / closure logic
- bridge reduction
- Sapiens packet generation
- engine-side reports and control suggestions

`CIEL-Desktop` consumes that truth through the desktop adapter layer.

## Global dependency direction

The intended dependency direction is:

`CIEL-_SOT_Agent` -> exported/reduced engine truth -> `CIEL-Desktop`

not the reverse.

This means the desktop layer should become thinner over time, not thicker.
The more explicit the engine contract becomes, the less direct import reach the desktop repo should need.

## Current transitional reality

At the current stage, `CIEL-Desktop` still uses a local adapter bridge into a checked-out copy of `CIEL-_SOT_Agent`.
That is acceptable as a transitional architecture, but it is not the final ideal state.

The long-term target is a smaller and more explicit engine contract surface, where the desktop layer consumes already-prepared state rather than importing broad internal engine modules.

## Human interpretation

A good human reading of the global system is:

- `CIEL-_SOT_Agent` = engine / canonical computation / truth source
- `CIEL-Desktop` = operator shell / presentation / controlled execution surface

## What “global” means here

Global does not mean vague ecosystem language.
It means the desktop repo must be understandable as a local chart inside the larger architecture.
A local repository index is useful, but only if it connects upward into the broader system role.

That is the purpose of this document.

## Merge implication

When PR #2 is reviewed, it should be judged not only by whether the desktop UI looks coherent locally, but also by whether it respects the global dependency order:

- truth remains upstream
- operator surface remains downstream
- explicit actions remain explicit
- presentation does not silently become engine logic
