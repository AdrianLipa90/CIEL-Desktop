from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .config import ROOT_DIR
from .core.sot_adapter import build_orbital_bridge, build_panel_state, build_sync_report, resolve_sot_root


def build_runtime_evidence(
    sot_root: str | Path | None = None,
    *,
    execution_mode: str = "desktop_runtime",
    user_text: str = "Desktop runtime evidence probe",
    sapiens_id: str = "desktop-runtime-probe",
) -> dict[str, Any]:
    started = time.perf_counter()
    resolved_root = resolve_sot_root(sot_root)

    sync_started = time.perf_counter()
    sync = build_sync_report(resolved_root)
    sync_ms = (time.perf_counter() - sync_started) * 1000.0

    bridge_started = time.perf_counter()
    bridge = build_orbital_bridge(resolved_root)
    bridge_ms = (time.perf_counter() - bridge_started) * 1000.0

    panel_started = time.perf_counter()
    panel = build_panel_state(resolved_root, user_text=user_text, sapiens_id=sapiens_id)
    panel_ms = (time.perf_counter() - panel_started) * 1000.0

    total_ms = (time.perf_counter() - started) * 1000.0

    coherence = bridge.get("state_manifest", {}).get(
        "coherence",
        bridge.get("health_manifest", {}).get("system_health", 0.0),
    )
    evidence = {
        "repository_scope": "AdrianLipa90/CIEL-Desktop",
        "execution_mode": execution_mode,
        "status_label": "tested",
        "evidence_class": "run_and_measured",
        "evidence": {
            "boot_status": "ok",
            "gui_status": "not_run",
            "latency": {
                "cold_start_ms": total_ms,
                "bridge_build_ms": bridge_ms,
                "panel_build_ms": panel_ms,
                "sync_build_ms": sync_ms,
            },
            "resource_usage": {
                "memory_mb": None,
                "notes": "Memory telemetry not yet instrumented in this probe"
            },
            "error_log": [],
        },
        "performance_evidence": {
            "cold_start_ms": total_ms,
            "bridge_build_ms": bridge_ms,
            "panel_build_ms": panel_ms,
            "measured": True,
        },
        "blockers": [],
        "unknowns": [
            "GUI event-loop runtime was not exercised by this probe",
            "Audio, STT, TTS, and GGUF paths were not exercised by this probe",
            "Memory telemetry is not yet instrumented"
        ],
        "next_actions": [
            "Run native GUI entrypoint under measured conditions",
            "Add audio and local-model execution mode probes",
            "Feed this artifact into ciel_sot_agent.runtime_evidence_ingest"
        ],
        "artifacts": {
            "sync_report": sync,
            "bridge_report": bridge,
            "panel_state": panel,
            "sot_root": str(resolved_root),
            "desktop_root": str(ROOT_DIR),
            "coherence": coherence,
            "closure_defect": sync.get("closure_defect", 0.0),
        },
        "errors": [],
        "metrics": {
            "cold_start_ms": total_ms,
            "bridge_build_ms": bridge_ms,
            "panel_build_ms": panel_ms,
        },
    }
    return evidence


def write_runtime_evidence(
    output_path: str | Path,
    sot_root: str | Path | None = None,
    *,
    execution_mode: str = "desktop_runtime",
) -> dict[str, Any]:
    evidence = build_runtime_evidence(sot_root, execution_mode=execution_mode)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    return evidence
