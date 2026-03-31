from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

from .sot_adapter import build_orbital_bridge, build_panel_state, build_sync_report


def _output_dir(root: Path) -> Path:
    out = root / "integration" / "reports" / "native_gui_actions"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def run_operator_action(root: Path, action_key: str) -> dict[str, Any]:
    root = Path(root)
    ts = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    out_dir = _output_dir(root)
    if action_key == "run_sync":
        payload = build_sync_report(root)
        path = out_dir / "sync_report.latest.json"
        _write_json(path, payload)
        return {"label": "run_sync", "details": f"closure_defect={payload.get('closure_defect', 0.0):.6f}", "severity": "info", "ts": ts}
    if action_key == "run_orbital":
        payload = build_orbital_bridge(root)
        path = out_dir / "orbital_bridge.latest.json"
        _write_json(path, payload)
        mode = payload.get("recommended_control", {}).get("mode", "unknown")
        health = payload.get("health_manifest", {}).get("system_health", "—")
        return {"label": "run_orbital", "details": f"mode={mode}; system_health={health}", "severity": "info", "ts": ts}
    if action_key == "rebuild_packet":
        payload = build_panel_state(root, user_text="Desktop operator packet rebuild", sapiens_id="desktop-operator")
        path = out_dir / "panel_state.latest.json"
        _write_json(path, payload)
        return {"label": "rebuild_packet", "details": f"session_id={payload.get('session_id', '—')}", "severity": "info", "ts": ts}
    if action_key == "operator_cycle":
        sync_payload = build_sync_report(root)
        orbital_payload = build_orbital_bridge(root)
        panel_payload = build_panel_state(root, user_text="Desktop operator cycle", sapiens_id="desktop-operator")
        path = out_dir / "operator_cycle.latest.json"
        _write_json(path, {"sync_report": sync_payload, "orbital_bridge": orbital_payload, "panel_state": panel_payload, "generated_at": ts})
        return {"label": "operator_cycle", "details": f"closure_defect={sync_payload.get('closure_defect', 0.0):.6f}; mode={orbital_payload.get('recommended_control', {}).get('mode', 'unknown')}", "severity": "info", "ts": ts}
    raise ValueError(f"Unsupported action_key: {action_key}")
