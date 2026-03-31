# Architecture

## Split

- `CIEL-_SOT_Agent` is the canonical computational core.
- `CIEL-Desktop` is the native operator shell.

## Local adapter model

The desktop shell currently imports the engine from a local checkout referenced by `CIEL_SOT_AGENT_ROOT`.

This is an interim bridge.
The long-term target is a thinner, explicit contract surface exported by the engine.

## Runtime flow

1. Desktop resolves the local SOT Agent checkout.
2. Adapter loads engine functions.
3. Data service builds a local snapshot.
4. State engine reduces snapshot to UI metrics.
5. Operator actions call the engine and write action artifacts to the engine repo under `integration/reports/native_gui_actions/`.
