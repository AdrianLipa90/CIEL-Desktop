from __future__ import annotations

import sys
import types

from ciel_desktop.core import sot_adapter
from ciel_desktop.core.sot_adapter import build_panel_state


def test_resolve_sot_root_prefers_current_repository_name(monkeypatch, tmp_path) -> None:
    desktop_root = tmp_path / "CIEL-Desktop"
    desktop_root.mkdir()
    current_sot_root = tmp_path / "CIEL-Omega-ApokalypOS"
    current_sot_root.mkdir()

    monkeypatch.delenv("CIEL_SOT_AGENT_ROOT", raising=False)
    monkeypatch.setattr(sot_adapter, "ROOT_DIR", desktop_root)

    assert sot_adapter.resolve_sot_root() == current_sot_root.resolve()


def test_build_panel_state_returns_render_dict(monkeypatch, tmp_path) -> None:
    pkg = types.ModuleType("ciel_sot_agent")
    pkg.__path__ = []
    subpkg = types.ModuleType("ciel_sot_agent.sapiens_panel")
    subpkg.__path__ = []
    controller = types.ModuleType("ciel_sot_agent.sapiens_panel.controller")
    render_schema = types.ModuleType("ciel_sot_agent.sapiens_panel.render_schema")

    class FakePanelState:
        pass

    controller.build_panel_state = lambda root, user_text, sapiens_id: FakePanelState()
    render_schema.to_render_dict = lambda state: {"session_id": "desktop-operator", "panel_state": {"mode": "standard"}}

    monkeypatch.setitem(sys.modules, "ciel_sot_agent", pkg)
    monkeypatch.setitem(sys.modules, "ciel_sot_agent.sapiens_panel", subpkg)
    monkeypatch.setitem(sys.modules, "ciel_sot_agent.sapiens_panel.controller", controller)
    monkeypatch.setitem(sys.modules, "ciel_sot_agent.sapiens_panel.render_schema", render_schema)

    result = build_panel_state(tmp_path, user_text="hello", sapiens_id="desktop-operator")

    assert isinstance(result, dict)
    assert result["session_id"] == "desktop-operator"