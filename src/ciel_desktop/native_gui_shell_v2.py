from __future__ import annotations

import json
import time
import tkinter as tk
from pathlib import Path
from tkinter.scrolledtext import ScrolledText
from typing import Any

from .native_gui_shell import (
    COLORS,
    FONTS,
    LAYOUT,
    ActionSurface,
    CIELNativeGUI,
    FocusObject,
    LeftRail,
    PlaceholderPanel,
    StateEngine,
    StateStrip,
    SystemMap,
    TemporalLayer,
    TopBar,
    DataService,
    bus,
    resolve_sot_root,
)


class MetricsPanel(tk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, bg=COLORS["bg"])
        self._data: dict[str, Any] = {}
        self._state: dict[str, Any] = {}
        self._build()
        bus.subscribe("data:updated", self._on_data)
        bus.subscribe("state:updated", self._on_state)

    def _build(self) -> None:
        hdr = tk.Frame(self, bg=COLORS["bg_panel"])
        hdr.pack(fill=tk.X)
        tk.Frame(hdr, bg=COLORS["border"], height=1).pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(hdr, text="METRICS", font=FONTS["title"], bg=COLORS["bg_panel"], fg=COLORS["cyan"], padx=16, pady=10).pack(side=tk.LEFT)

        self.summary = tk.Frame(self, bg=COLORS["bg"])
        self.summary.pack(fill=tk.X, padx=12, pady=12)

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        left = tk.Frame(body, bg=COLORS["bg_panel"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        tk.Label(left, text="PAIRWISE TENSIONS", font=FONTS["label"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(anchor="w", padx=10, pady=(8, 4))
        self.tensions = ScrolledText(left, font=FONTS["mono_xs"], bg=COLORS["bg_panel"], fg=COLORS["text"], relief=tk.FLAT)
        self.tensions.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        right = tk.Frame(body, bg=COLORS["bg_panel"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(right, text="BRIDGE / HEALTH", font=FONTS["label"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(anchor="w", padx=10, pady=(8, 4))
        self.bridge = ScrolledText(right, font=FONTS["mono_xs"], bg=COLORS["bg_panel"], fg=COLORS["text"], relief=tk.FLAT)
        self.bridge.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _render_summary(self) -> None:
        for child in self.summary.winfo_children():
            child.destroy()
        rows = [
            ("coherence", self._state.get("coherence", "—")),
            ("defect", self._state.get("defect", "—")),
            ("energy", self._state.get("energy", "—")),
            ("tension", self._state.get("tension", "—")),
            ("mode", self._state.get("mode", "—")),
            ("state", self._state.get("state", "—")),
        ]
        for key, value in rows:
            box = tk.Frame(self.summary, bg=COLORS["bg_panel"], padx=10, pady=8)
            box.pack(side=tk.LEFT, padx=(0, 10))
            tk.Label(box, text=key, font=FONTS["label"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(anchor="w")
            tk.Label(box, text=str(value), font=FONTS["mono_lg"], bg=COLORS["bg_panel"], fg=COLORS["cyan"]).pack(anchor="w")

    def _render_tensions(self) -> None:
        sync_report = self._data.get("sync_report", {})
        rows = sync_report.get("pairwise_tensions", []) or []
        self.tensions.delete("1.0", tk.END)
        if not rows:
            self.tensions.insert("1.0", "No pairwise tensions available.\n")
            return
        for row in rows:
            line = (
                f"{row.get('source', '—')} -> {row.get('target', '—')}"
                f"  tension={row.get('tension', '—')}"
                f"  coupling={row.get('coupling_weight', '—')}"
            )
            self.tensions.insert(tk.END, line + "\n")

    def _render_bridge(self) -> None:
        bridge = self._data.get("bridge_summary", {})
        sync_report = self._data.get("sync_report", {})
        text = {
            "weighted_euler_vector": sync_report.get("weighted_euler_vector", "—"),
            "closure_defect": sync_report.get("closure_defect", "—"),
            "system_health": bridge.get("health_manifest", {}).get("system_health", "—"),
            "recommended_action": bridge.get("health_manifest", {}).get("recommended_action", "—"),
            "mode": bridge.get("recommended_control", {}).get("mode", "—"),
            "T_glob": bridge.get("health_manifest", {}).get("T_glob", bridge.get("health_manifest", {}).get("tension_global", "—")),
        }
        self.bridge.delete("1.0", tk.END)
        self.bridge.insert("1.0", json.dumps(text, indent=2, ensure_ascii=False))

    def _on_data(self, data: dict[str, Any]) -> None:
        self._data = data
        self._render_tensions()
        self._render_bridge()

    def _on_state(self, state: dict[str, Any]) -> None:
        self._state = state
        self._render_summary()


class ReportsPanel(tk.Frame):
    def __init__(self, parent: tk.Misc, root_dir: Path) -> None:
        super().__init__(parent, bg=COLORS["bg"])
        self._root = root_dir
        self._data: dict[str, Any] = {}
        self._selected: str | None = None
        self._build()
        bus.subscribe("data:updated", self._on_data)

    def _build(self) -> None:
        hdr = tk.Frame(self, bg=COLORS["bg_panel"])
        hdr.pack(fill=tk.X)
        tk.Frame(hdr, bg=COLORS["border"], height=1).pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(hdr, text="REPORTS", font=FONTS["title"], bg=COLORS["bg_panel"], fg=COLORS["cyan"], padx=16, pady=10).pack(side=tk.LEFT)

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        left = tk.Frame(body, bg=COLORS["bg_panel"], width=360)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left.pack_propagate(False)
        tk.Label(left, text="RECENT REPORTS", font=FONTS["label"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(anchor="w", padx=10, pady=(8, 4))
        self.listbox = tk.Listbox(left, font=FONTS["mono_xs"], bg=COLORS["bg_input"], fg=COLORS["text"], relief=tk.FLAT, activestyle="none")
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        right = tk.Frame(body, bg=COLORS["bg_panel"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(right, text="PREVIEW", font=FONTS["label"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(anchor="w", padx=10, pady=(8, 4))
        self.preview = ScrolledText(right, font=FONTS["mono_xs"], bg=COLORS["bg_panel"], fg=COLORS["text"], relief=tk.FLAT)
        self.preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _refresh_list(self) -> None:
        self.listbox.delete(0, tk.END)
        reports = self._data.get("reports", [])
        for row in reports[:100]:
            label = f"{row.get('name', '—')}  ({row.get('size', 0)} B)"
            self.listbox.insert(tk.END, label)
        if reports and self._selected is None:
            self._selected = reports[0].get("path")
            self._render_preview()

    def _render_preview(self) -> None:
        self.preview.delete("1.0", tk.END)
        if not self._selected:
            self.preview.insert("1.0", "No report selected.\n")
            return
        path = self._root / self._selected
        if not path.exists():
            self.preview.insert("1.0", f"Missing file: {self._selected}\n")
            return
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            self.preview.insert("1.0", f"Could not read {self._selected}: {exc}\n")
            return
        header = f"path: {self._selected}\nmtime: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(path.stat().st_mtime))}\n\n"
        self.preview.insert("1.0", header + text[:20000])

    def _on_select(self, _event: Any) -> None:
        idxs = self.listbox.curselection()
        if not idxs:
            return
        idx = idxs[0]
        reports = self._data.get("reports", [])
        if idx >= len(reports):
            return
        self._selected = reports[idx].get("path")
        self._render_preview()

    def _on_data(self, data: dict[str, Any]) -> None:
        self._data = data
        self._refresh_list()
        self._render_preview()


class CIELNativeGUIV2(CIELNativeGUI):
    def __init__(self, root_dir: str | Path | None = None) -> None:
        super().__init__(root_dir)
        self.title("CIEL Desktop · Native GUI v2")

    def _build_shell(self) -> None:
        self._topbar = TopBar(self, self._state_engine)
        self._topbar.pack(side=tk.TOP, fill=tk.X)
        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill=tk.BOTH, expand=True)
        self._left = LeftRail(body)
        self._left.pack(side=tk.LEFT, fill=tk.Y)
        self._workspace = tk.Frame(body, bg=COLORS["bg"])
        self._workspace.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._focus = FocusObject(body)
        self._focus.pack(side=tk.RIGHT, fill=tk.Y)
        self._focus.config(width=LAYOUT["right_drawer"])
        self._focus.pack_propagate(False)
        self._build_panels()

    def _build_panels(self) -> None:
        control = tk.Frame(self._workspace, bg=COLORS["bg"])
        StateStrip(control).pack(side=tk.TOP, fill=tk.X)
        operational = tk.Frame(control, bg=COLORS["bg"])
        operational.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        SystemMap(operational).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ActionSurface(operational, self._state_engine, self._root_dir, self._data_service).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        TemporalLayer(control).pack(side=tk.BOTTOM, fill=tk.X)
        self._panels = {
            "Control": control,
            "Metrics": MetricsPanel(self._workspace),
            "Reports": ReportsPanel(self._workspace, self._root_dir),
            "Support": PlaceholderPanel(
                self._workspace,
                "SUPPORT",
                "Native GUI shell v2 running against local CIEL-_SOT_Agent checkout.\n\nUse `scripts/run_ciel_native_gui_v2.py` to launch this richer shell.\nSet CIEL_SOT_AGENT_ROOT if the engine is not adjacent to this repo.",
            ),
        }
        for panel in self._panels.values():
            panel.pack_forget()


def main() -> None:
    app = CIELNativeGUIV2(Path.cwd())
    app.mainloop()


if __name__ == "__main__":
    main()
