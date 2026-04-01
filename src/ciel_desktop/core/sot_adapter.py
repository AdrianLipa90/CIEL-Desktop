from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from ..config import ROOT_DIR, SOT_AGENT_ENV


def resolve_sot_root(explicit_root: str | Path | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    env_root = os.getenv(SOT_AGENT_ENV)
    if env_root:
        return Path(env_root).resolve()
    candidate = ROOT_DIR.parent / "CIEL-_SOT_Agent"
    if candidate.exists():
        return candidate.resolve()
    raise RuntimeError(
        "CIEL SOT Agent root not found. Set CIEL_SOT_AGENT_ROOT to a local checkout of AdrianLipa90/CIEL-_SOT_Agent."
    )


def _ensure_import_path(root: Path) -> None:
    src_dir = root / "src"
    for path in (root, src_dir):
        p = str(path)
        if p not in sys.path:
            sys.path.insert(0, p)


def build_sync_report(root: Path) -> dict[str, Any]:
    root = resolve_sot_root(root)
    _ensure_import_path(root)
    from ciel_sot_agent.repo_phase import build_sync_report as _impl
    return _impl(root / "integration" / "repository_registry.json", root / "integration" / "couplings.json")


def build_orbital_bridge(root: Path) -> dict[str, Any]:
    root = resolve_sot_root(root)
    _ensure_import_path(root)
    from ciel_sot_agent.orbital_bridge import build_orbital_bridge as _impl
    return _impl(root)


def build_panel_state(root: Path, user_text: str, sapiens_id: str) -> dict[str, Any]:
    root = resolve_sot_root(root)
    _ensure_import_path(root)
    from ciel_sot_agent.sapiens_panel.controller import build_panel_state as _impl
    from ciel_sot_agent.sapiens_panel.render_schema import to_render_dict

    state = _impl(root, user_text=user_text, sapiens_id=sapiens_id)
    return to_render_dict(state)
