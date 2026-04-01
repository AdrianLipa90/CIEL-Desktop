from __future__ import annotations

import argparse
import json
from pathlib import Path

from ciel_desktop.runtime_evidence_probe import write_runtime_evidence


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the desktop runtime evidence probe.")
    parser.add_argument(
        "--output",
        default="runtime_evidence/desktop_runtime_evidence.json",
        help="Where to write the runtime evidence artifact.",
    )
    parser.add_argument(
        "--sot-root",
        default=None,
        help="Path to local CIEL-_SOT_Agent checkout.",
    )
    parser.add_argument(
        "--mode",
        default="desktop_runtime",
        help="Execution mode label for the evidence artifact.",
    )
    args = parser.parse_args()

    evidence = write_runtime_evidence(Path(args.output), args.sot_root, execution_mode=args.mode)
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
