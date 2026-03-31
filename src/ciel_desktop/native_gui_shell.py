from __future__ import annotations

import json
import math
import threading
import time
import tkinter as tk
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from tkinter.scrolledtext import ScrolledText
from typing import Any, Callable

import yaml

from .core.operator_actions import run_operator_action
from .core.sot_adapter import build_orbital_bridge, build_panel_state, build_sync_report, resolve_sot_root

APP_TITLE = "CIEL Desktop · Native GUI"
APP_GEOMETRY = "1500x920"
REFRESH_MS = 30_000

COLORS = {
    "bg": "#0e0e0e",
    "bg_panel": "#141414",
    "bg_input": "#1a1a1a",
    "border": "#242424",
    "border_active": "#2e2e2e",
    "text": "#c8c8c8",
    "text_dim": "#6a6a6a",
    "text_label": "#8a8a8a",
    "cyan": "#00c0c0",
    "amber": "#c89000",
    "red": "#c03030",
    "violet": "#7040a0",
    "green": "#408050",
}

FONTS = {
    "mono": ("Courier New", 10),
    "mono_sm": ("Courier New", 9),
    "mono_xs": ("Courier New", 8),
    "mono_lg": ("Courier New", 12, "bold"),
    "title": ("Courier New", 10, "bold"),
    "label": ("Courier New", 8),
}

LAYOUT = {
    "top_bar": 44,
    "state_strip": 68,
    "left_rail": 220,
    "right_drawer": 320,
    "temporal": 180,
}


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[str, list[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable[[Any], None]) -> None:
        self._subs[event].append(callback)

    def publish(self, event: str, payload: Any = None) -> None:
        for cb in list(self._subs.get(event, [])):
            try:
                cb(payload)
            except Exception as exc:
                print(f"[EventBus] {event} handler error: {exc}")


bus = EventBus()


@dataclass
class DataService:
    root: Path

    def __post_init__(self) -> None:
        self.root = resolve_sot_root(self.root)
        self._cache: dict[str, Any] = {}
        self._lock = threading.Lock()

    def _load_json(self, relative_path: str, fallback: Any) -> Any:
        path = self.root / relative_path
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))

    def _load_yaml(self, relative_path: str, fallback: Any) -> Any:
        path = self.root / relative_path
        if not path.exists():
            return fallback
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def _list_reports(self) -> list[dict[str, Any]]:
        report_root = self.root / "integration" / "reports"
        rows: list[dict[str, Any]] = []
        if not report_root.exists():
            return rows
        for path in sorted(report_root.rglob("*")):
            if not path.is_file():
                continue
            rows.append(
                {
                    "path": str(path.relative_to(self.root)),
                    "name": path.name,
                    "size": path.stat().st_size,
                    "mtime": path.stat().st_mtime,
                }
            )
        rows.sort(key=lambda item: item["mtime"], reverse=True)
        return rows

    def _build_timeline(self, reports: list[dict[str, Any]], sync_report: dict[str, Any], bridge: dict[str, Any], panel_state: dict[str, Any]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        items.append({
            "ts": time.strftime("%H:%M:%S"),
            "kind": "state",
            "label": f"closure_defect={sync_report.get('closure_defect', 0.0):.6f}",
            "details": "repo phase refresh",
        })
        items.append({
            "ts": time.strftime("%H:%M:%S"),
            "kind": "state",
            "label": f"mode={bridge.get('recommended_control', {}).get('mode', 'unknown')}",
            "details": f"system_health={bridge.get('health_manifest', {}).get('system_health', '—')}",
        })
        if panel_state:
            items.append({
                "ts": time.strftime("%H:%M:%S"),
                "kind": "packet",
                "label": f"session_id={panel_state.get('session_id', '—')}",
                "details": "panel state build",
            })
        for row in reports[:8]:
            items.append({
                "ts": time.strftime("%H:%M:%S", time.localtime(row.get("mtime", 0))),
                "kind": "report",
                "label": row.get("name", "—"),
                "details": row.get("path", "—"),
            })
        return items

    def build_snapshot(self) -> dict[str, Any]:
        sync_report = build_sync_report(self.root)
        bridge_summary = build_orbital_bridge(self.root)
        panel_state = build_panel_state(self.root, user_text="Native GUI shell", sapiens_id="desktop-operator")
        index_registry = self._load_yaml("integration/index_registry.yaml", {})
        hyperspace_index = self._load_json("integration/hyperspace_index.json", {})
        reports = self._list_reports()
        timeline = self._build_timeline(reports, sync_report, bridge_summary, panel_state)
        objects = list(index_registry.get("objects", [])) if isinstance(index_registry, dict) else []
        return {
            "repo_root": str(self.root),
            "sync_report": sync_report,
            "bridge_summary": bridge_summary,
            "panel_state": panel_state,
            "index_registry": index_registry,
            "hyperspace_index": hyperspace_index,
            "reports": reports,
            "timeline": timeline,
            "objects": objects,
        }

    def refresh(self) -> None:
        bus.publish("status:fetching", True)

        def _worker() -> None:
            payload = self.build_snapshot()
            with self._lock:
                self._cache = payload
            bus.publish("data:updated", payload)
            bus.publish("status:fetching", False)

        threading.Thread(target=_worker, daemon=True).start()


class StateEngine:
    def __init__(self) -> None:
        self._s = {
            "coherence": 0.0,
            "defect": 0.0,
            "energy": 0.0,
            "tension": 0.0,
            "state": "initializing",
            "mode": "safe",
            "writeback": "closed",
            "queue": 0,
            "alerts": [],
            "updated": "—",
        }
        self._prev: dict[str, Any] = {}
        bus.subscribe("data:updated", self._on_data)

    def _on_data(self, data: dict[str, Any]) -> None:
        self._prev = dict(self._s)
        self._compute(data)
        bus.publish("state:updated", self._with_deltas())

    def _compute(self, data: dict[str, Any]) -> None:
        bridge = data.get("bridge_summary", {})
        sync_report = data.get("sync_report", {})
        panel = data.get("panel_state", {})
        reports = data.get("reports", [])
        state_manifest = bridge.get("state_manifest", {})
        health = bridge.get("health_manifest", {})
        control = bridge.get("recommended_control", {})
        pairwise = sync_report.get("pairwise_tensions", [])

        coherence = float(state_manifest.get("coherence_index", state_manifest.get("coherence", 0.0)))
        defect = float(sync_report.get("closure_defect", 1.0))
        tension = max(float(health.get("T_glob", 0.0)), max((float(row.get("tension", 0.0)) for row in pairwise), default=0.0))
        energy = min(1.0, max(0.0, 0.45 * float(health.get("system_health", 0.0)) + 0.35 * min(1.0, len(reports) / 20) + 0.20 * (1.0 if panel else 0.0)))
        mode = str(control.get("mode", "standard"))
        writeback = "open" if mode in ("standard", "deep") else "closed"

        alerts: list[tuple[str, str]] = []
        if defect > 0.03:
            alerts.append(("closure defect elevated", "amber"))
        if tension > 0.5:
            alerts.append(("global tension high", "red"))
        if coherence < 0.75:
            alerts.append(("coherence below target", "amber"))

        if coherence >= 0.9 and defect <= 0.01:
            state = "stable"
        elif tension >= 0.6:
            state = "unstable"
        elif defect > 0.02:
            state = "drifting"
        else:
            state = "constrained"

        self._s.update(
            {
                "coherence": round(coherence, 3),
                "defect": round(defect, 6),
                "energy": round(energy, 3),
                "tension": round(tension, 3),
                "state": state,
                "mode": mode,
                "writeback": writeback,
                "queue": len(reports),
                "alerts": alerts,
                "updated": time.strftime("%H:%M:%S"),
            }
        )

    def _with_deltas(self) -> dict[str, Any]:
        out = dict(self._s)
        for key in ("coherence", "defect", "energy", "tension"):
            out[f"d_{key}"] = round(float(self._s[key]) - float(self._prev.get(key, self._s[key])), 6)
        return out

    def set_mode(self, mode: str) -> None:
        if mode in ("safe", "standard", "deep"):
            self._s["mode"] = mode
            self._s["writeback"] = "open" if mode in ("standard", "deep") else "closed"
            bus.publish("state:updated", self._with_deltas())

    def toggle_writeback(self) -> None:
        self._s["writeback"] = "open" if self._s["writeback"] == "closed" else "closed"
        bus.publish("state:updated", self._with_deltas())


class TopBar(tk.Frame):
    def __init__(self, parent: tk.Misc, state_engine: StateEngine) -> None:
        super().__init__(parent, bg=COLORS["bg_panel"], height=LAYOUT["top_bar"])
        self.pack_propagate(False)
        self._build()
        bus.subscribe("state:updated", self._on_state)
        bus.subscribe("status:fetching", self._on_fetch)
        bus.subscribe("data:updated", self._on_data)

    def _build(self) -> None:
        tk.Frame(self, bg=COLORS["border"], height=1).pack(side=tk.BOTTOM, fill=tk.X)
        wrap = tk.Frame(self, bg=COLORS["bg_panel"])
        wrap.pack(fill=tk.BOTH, expand=True, padx=10)
        left = tk.Frame(wrap, bg=COLORS["bg_panel"])
        left.pack(side=tk.LEFT)
        tk.Label(left, text="CIEL", font=FONTS["title"], bg=COLORS["bg_panel"], fg=COLORS["cyan"]).pack(side=tk.LEFT, padx=(0, 8))
        self.lbl_repo = self._lbl(left, "repo: …")
        center = tk.Frame(wrap, bg=COLORS["bg_panel"])
        center.pack(side=tk.LEFT, expand=True, padx=20)
        self.lbl_mode = self._lbl(center, "mode: safe", COLORS["cyan"])
        self.lbl_wb = self._lbl(center, "writeback: closed", COLORS["amber"])
        self.lbl_backend = self._lbl(center, "backend: local", COLORS["text_dim"])
        right = tk.Frame(wrap, bg=COLORS["bg_panel"])
        right.pack(side=tk.RIGHT)
        self.lbl_energy = self._lbl(right, "energy: —")
        self.lbl_alerts = self._lbl(right, "alerts: 0")
        self.lbl_time = self._lbl(right, "—")
        self._tick()

    def _lbl(self, parent: tk.Misc, text: str, fg: str | None = None) -> tk.Label:
        lbl = tk.Label(parent, text=text, font=FONTS["mono_sm"], bg=COLORS["bg_panel"], fg=fg or COLORS["text_dim"])
        lbl.pack(side=tk.LEFT, padx=4)
        return lbl

    def _on_state(self, state: dict[str, Any]) -> None:
        self.lbl_mode.config(text=f"mode: {state.get('mode', '—')}", fg=COLORS["cyan"])
        wb = state.get("writeback", "closed")
        self.lbl_wb.config(text=f"writeback: {wb}", fg=COLORS["green"] if wb == "open" else COLORS["amber"])
        self.lbl_energy.config(text=f"energy: {float(state.get('energy', 0.0)):.0%}")
        alerts = state.get("alerts", [])
        self.lbl_alerts.config(text=f"alerts: {len(alerts)}", fg=COLORS["red"] if alerts else COLORS["text_dim"])

    def _on_fetch(self, fetching: bool) -> None:
        self.lbl_backend.config(text="backend: refreshing" if fetching else "backend: local", fg=COLORS["amber"] if fetching else COLORS["text_dim"])

    def _on_data(self, data: dict[str, Any]) -> None:
        self.lbl_repo.config(text=f"repo: {Path(data.get('repo_root', '—')).name}", fg=COLORS["cyan"])

    def _tick(self) -> None:
        self.lbl_time.config(text=time.strftime("%H:%M:%S"))
        self.after(1000, self._tick)


class LeftRail(tk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, bg=COLORS["bg_panel"], width=LAYOUT["left_rail"])
        self.pack_propagate(False)
        self._active = "Control"
        self._btns: dict[str, tk.Label] = {}
        self._build()

    def _build(self) -> None:
        for name in ["Control", "Metrics", "Reports", "Support"]:
            lbl = tk.Label(self, text=f"  ▸  {name}", font=FONTS["mono"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"], anchor="w", pady=9, cursor="hand2")
            lbl.pack(fill=tk.X, padx=6, pady=1)
            lbl.bind("<Button-1>", lambda _e, n=name: self._select(n))
            self._btns[name] = lbl
        self._select("Control")

    def _select(self, name: str) -> None:
        for key, lbl in self._btns.items():
            active = key == name
            lbl.config(bg=COLORS["bg_input"] if active else COLORS["bg_panel"], fg=COLORS["cyan"] if active else COLORS["text_dim"])
        self._active = name
        bus.publish("nav:changed", name)


class StateStrip(tk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, bg=COLORS["bg_panel"], height=LAYOUT["state_strip"])
        self.pack_propagate(False)
        self._widgets: dict[str, tuple[tk.Label, tk.Label]] = {}
        self._build()
        bus.subscribe("state:updated", self._on_state)

    def _build(self) -> None:
        tk.Frame(self, bg=COLORS["border"], height=1).pack(side=tk.BOTTOM, fill=tk.X)
        inner = tk.Frame(self, bg=COLORS["bg_panel"])
        inner.pack(fill=tk.BOTH, expand=True, padx=16)
        for key in ["coherence", "defect", "energy", "tension", "state", "mode"]:
            col = tk.Frame(inner, bg=COLORS["bg_panel"])
            col.pack(side=tk.LEFT, padx=18, pady=8)
            tk.Label(col, text=key, font=FONTS["label"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(anchor="w")
            val = tk.Label(col, text="—", font=FONTS["mono_lg"], bg=COLORS["bg_panel"], fg=COLORS["cyan"])
            val.pack(anchor="w")
            delta = tk.Label(col, text="·", font=FONTS["mono_xs"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"])
            delta.pack(anchor="w")
            self._widgets[key] = (val, delta)

    def _on_state(self, state: dict[str, Any]) -> None:
        for key, (val, delta) in self._widgets.items():
            value = state.get(key, "—")
            val.config(text=f"{value:.3f}" if isinstance(value, float) else str(value))
            dk = state.get(f"d_{key}")
            if dk is None:
                delta.config(text="·")
            else:
                delta.config(text=f"Δ {dk:+.6f}" if abs(dk) < 1 else f"Δ {dk:+.3f}")


class SystemMap(tk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, bg=COLORS["bg"])
        self._data: dict[str, Any] = {}
        self._state: dict[str, Any] = {}
        self._anim_t = 0.0
        tk.Label(self, text="SYSTEM MAP", font=FONTS["label"], bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(anchor="w", padx=10, pady=(8, 0))
        self.cv = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0)
        self.cv.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.cv.bind("<Configure>", self._redraw)
        bus.subscribe("data:updated", self._on_data)
        bus.subscribe("state:updated", self._on_state)
        self._animate()

    def _on_data(self, data: dict[str, Any]) -> None:
        self._data = data
        self._redraw()

    def _on_state(self, state: dict[str, Any]) -> None:
        self._state = state
        self._redraw()

    def _redraw(self, _event: Any = None) -> None:
        self.cv.delete("all")
        w = max(1, self.cv.winfo_width())
        h = max(1, self.cv.winfo_height())
        cx, cy = w // 2, h // 2
        r = min(w, h) // 3
        nodes = {
            "repo": (cx, cy - r * 0.65, COLORS["cyan"], Path(self._data.get("repo_root", "repo")).name),
            "orbital": (cx + r * 0.7 * math.cos(self._anim_t * 0.4), cy + r * 0.2, COLORS["violet"], "orbital"),
            "bridge": (cx - r * 0.7, cy + r * 0.35, COLORS["amber"], "bridge"),
            "sapiens": (cx + r * 0.6, cy + r * 0.55, COLORS["green"], "sapiens"),
        }
        edges = [("repo", "orbital"), ("repo", "bridge"), ("repo", "sapiens"), ("orbital", "sapiens"), ("bridge", "sapiens")]
        for a, b in edges:
            x1, y1, _, _ = nodes[a]
            x2, y2, _, _ = nodes[b]
            self.cv.create_line(x1, y1, x2, y2, fill=COLORS["border_active"], dash=(3, 5))
        for key, (x, y, color, label) in nodes.items():
            self.cv.create_oval(x - 8, y - 8, x + 8, y + 8, fill=color, outline="")
            self.cv.create_text(x, y - 16, text=label, font=FONTS["mono_xs"], fill=color)
        state_color = {
            "stable": COLORS["cyan"],
            "drifting": COLORS["amber"],
            "unstable": COLORS["red"],
            "constrained": COLORS["violet"],
        }.get(self._state.get("state", ""), COLORS["border"])
        pulse = 18 + 4 * math.sin(self._anim_t * 2)
        self.cv.create_oval(cx - pulse, cy - pulse, cx + pulse, cy + pulse, outline=state_color)
        self.cv.create_text(cx, cy, text=self._state.get("state", "—"), font=FONTS["mono_xs"], fill=state_color)

    def _animate(self) -> None:
        self._anim_t += 0.05
        self._redraw()
        self.after(80, self._animate)


class ActionSurface(tk.Frame):
    def __init__(self, parent: tk.Misc, state_engine: StateEngine, root: Path, data_service: DataService) -> None:
        super().__init__(parent, bg=COLORS["bg"])
        self._se = state_engine
        self._root = root
        self._data_service = data_service
        self.rec_container: tk.Frame | None = None
        self._build()
        bus.subscribe("state:updated", self._on_state)

    def _build(self) -> None:
        gate = tk.Frame(self, bg=COLORS["bg_panel"])
        gate.pack(fill=tk.X, padx=8, pady=(8, 4))
        tk.Label(gate, text="GATE STATUS", font=FONTS["label"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(anchor="w", padx=8, pady=(6, 2))
        row = tk.Frame(gate, bg=COLORS["bg_panel"])
        row.pack(fill=tk.X, padx=8, pady=4)
        self.lbl_gate = tk.Label(row, text="writeback: closed", font=FONTS["mono_xs"], bg=COLORS["bg_input"], fg=COLORS["amber"], padx=5, pady=1)
        self.lbl_gate.pack(side=tk.LEFT, padx=4)
        self.lbl_mode = tk.Label(row, text="mode: safe", font=FONTS["mono_xs"], bg=COLORS["bg_input"], fg=COLORS["cyan"], padx=5, pady=1)
        self.lbl_mode.pack(side=tk.LEFT, padx=4)
        for mode in ("safe", "standard", "deep"):
            tk.Button(gate, text=f"set {mode}", font=FONTS["mono_xs"], bg=COLORS["bg_input"], fg=COLORS["text_dim"], relief=tk.FLAT, command=lambda m=mode: self._set_mode(m)).pack(side=tk.LEFT, padx=2, pady=6)
        tk.Button(gate, text="toggle writeback", font=FONTS["mono_xs"], bg=COLORS["bg_input"], fg=COLORS["amber"], relief=tk.FLAT, command=self._toggle_wb).pack(side=tk.RIGHT, padx=8, pady=6)
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill=tk.X, padx=8)
        rec = tk.Frame(self, bg=COLORS["bg"])
        rec.pack(fill=tk.X, padx=8, pady=(6, 4))
        tk.Label(rec, text="RECOMMENDED ACTIONS", font=FONTS["label"], bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(anchor="w", pady=(4, 2))
        self.rec_container = tk.Frame(rec, bg=COLORS["bg"])
        self.rec_container.pack(fill=tk.X)
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill=tk.X, padx=8)
        qa = tk.Frame(self, bg=COLORS["bg"])
        qa.pack(fill=tk.X, padx=8, pady=(6, 4))
        tk.Label(qa, text="QUICK ACTIONS", font=FONTS["label"], bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(anchor="w", pady=(4, 2))
        for action_key, label, desc in [
            ("run_sync", "run sync", "→ repo phase refresh"),
            ("run_orbital", "run orbital pass", "→ bridge recompute"),
            ("rebuild_packet", "rebuild packet", "→ panel state build"),
            ("operator_cycle", "operator cycle", "→ full operator run"),
            ("refresh", "refresh data", "→ local snapshot rebuild"),
        ]:
            row = tk.Frame(qa, bg=COLORS["bg"])
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=f"  ▹  {label}", font=FONTS["mono_sm"], bg=COLORS["bg"], fg=COLORS["text"], anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=desc, font=FONTS["mono_xs"], bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(side=tk.LEFT, padx=6)
            tk.Button(row, text="run", font=FONTS["mono_xs"], bg=COLORS["bg_input"], fg=COLORS["cyan"], relief=tk.FLAT, command=lambda a=action_key: self._run(a)).pack(side=tk.RIGHT, padx=4)
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill=tk.X, padx=8)
        self.log_box = ScrolledText(self, height=7, font=FONTS["mono_xs"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"], relief=tk.FLAT)
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=(6, 8))

    def _set_mode(self, mode: str) -> None:
        self._se.set_mode(mode)
        self._log(f"mode set -> {mode}")

    def _toggle_wb(self) -> None:
        self._se.toggle_writeback()
        self._log("writeback toggled")

    def _run(self, action_key: str) -> None:
        if action_key == "refresh":
            self._data_service.refresh()
            self._log("refresh requested")
            return
        result = run_operator_action(self._root, action_key)
        self._log(f"{result.get('label', action_key)} -> {result.get('details', '—')}")
        self._data_service.refresh()

    def _log(self, text: str) -> None:
        self.log_box.insert("1.0", f"[{time.strftime('%H:%M:%S')}] {text}\n")

    def _on_state(self, state: dict[str, Any]) -> None:
        wb = state.get("writeback", "closed")
        self.lbl_gate.config(text=f"writeback: {wb}", fg=COLORS["green"] if wb == "open" else COLORS["amber"])
        self.lbl_mode.config(text=f"mode: {state.get('mode', '—')}")
        if self.rec_container is None:
            return
        for child in self.rec_container.winfo_children():
            child.destroy()
        recs: list[tuple[str, str]] = []
        if float(state.get("defect", 0.0)) > 0.02:
            recs.append(("stabilize defect", "run sync"))
        if float(state.get("tension", 0.0)) > 0.5:
            recs.append(("inspect bridge", "run orbital"))
        if not recs:
            recs.append(("system nominal", "no immediate action"))
        for label, desc in recs:
            tk.Label(self.rec_container, text=f"  · {label} — {desc}", font=FONTS["mono_xs"], bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(anchor="w", padx=8)


class FocusObject(tk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, bg=COLORS["bg_panel"])
        self._data: dict[str, Any] = {}
        self._state: dict[str, Any] = {}
        tk.Frame(self, bg=COLORS["border"], width=1).pack(side=tk.LEFT, fill=tk.Y)
        inner = tk.Frame(self, bg=COLORS["bg_panel"])
        inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(inner, text="FOCUS OBJECT", font=FONTS["label"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(anchor="w")
        self.lbl_name = tk.Label(inner, text="repo", font=FONTS["mono_lg"], bg=COLORS["bg_panel"], fg=COLORS["cyan"])
        self.lbl_name.pack(anchor="w")
        self.body = ScrolledText(inner, font=FONTS["mono_xs"], bg=COLORS["bg_input"], fg=COLORS["text_dim"], relief=tk.FLAT)
        self.body.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        bus.subscribe("data:updated", self._on_data)
        bus.subscribe("state:updated", self._on_state)

    def _render(self) -> None:
        repo_root = Path(self._data.get("repo_root", "repo")).name
        sync_report = self._data.get("sync_report", {})
        bridge = self._data.get("bridge_summary", {})
        panel = self._data.get("panel_state", {})
        self.lbl_name.config(text=repo_root)
        text = (
            f"closure_defect: {sync_report.get('closure_defect', '—')}\n"
            f"weighted_euler_vector: {sync_report.get('weighted_euler_vector', '—')}\n"
            f"mode: {bridge.get('recommended_control', {}).get('mode', '—')}\n"
            f"system_health: {bridge.get('health_manifest', {}).get('system_health', '—')}\n"
            f"recommended_action: {bridge.get('health_manifest', {}).get('recommended_action', '—')}\n"
            f"session_id: {panel.get('session_id', '—')}\n"
            f"alerts: {len(self._state.get('alerts', []))}\n"
        )
        self.body.delete("1.0", tk.END)
        self.body.insert("1.0", text)

    def _on_data(self, data: dict[str, Any]) -> None:
        self._data = data
        self._render()

    def _on_state(self, state: dict[str, Any]) -> None:
        self._state = state
        self._render()


class TemporalLayer(tk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, bg=COLORS["bg_panel"], height=LAYOUT["temporal"])
        self.pack_propagate(False)
        tk.Frame(self, bg=COLORS["border"], height=1).pack(side=tk.TOP, fill=tk.X)
        tk.Label(self, text="TEMPORAL LAYER", font=FONTS["label"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(anchor="w", padx=10, pady=(6, 0))
        self.box = ScrolledText(self, height=8, font=FONTS["mono_xs"], bg=COLORS["bg_input"], fg=COLORS["text_dim"], relief=tk.FLAT)
        self.box.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        bus.subscribe("data:updated", self._on_data)

    def _on_data(self, data: dict[str, Any]) -> None:
        self.box.delete("1.0", tk.END)
        for item in data.get("timeline", [])[:12]:
            line = f"[{item.get('ts', '—')}] {item.get('kind', 'event'):<8} {item.get('label', '—')}"
            details = item.get("details", "")
            if details:
                line += f"\n    {details}"
            self.box.insert(tk.END, line + "\n")


class PlaceholderPanel(tk.Frame):
    def __init__(self, parent: tk.Misc, title: str, description: str) -> None:
        super().__init__(parent, bg=COLORS["bg"])
        hdr = tk.Frame(self, bg=COLORS["bg_panel"])
        hdr.pack(fill=tk.X)
        tk.Frame(hdr, bg=COLORS["border"], height=1).pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(hdr, text=title, font=FONTS["title"], bg=COLORS["bg_panel"], fg=COLORS["cyan"], padx=16, pady=10).pack(side=tk.LEFT)
        body = ScrolledText(self, font=FONTS["mono_xs"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"], relief=tk.FLAT)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        body.insert("1.0", description)


class CIELNativeGUI(tk.Tk):
    def __init__(self, root_dir: str | Path | None = None) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.configure(bg=COLORS["bg"])
        self.geometry(APP_GEOMETRY)
        self.minsize(1260, 760)
        self._root_dir = resolve_sot_root(root_dir)
        self._state_engine = StateEngine()
        self._data_service = DataService(self._root_dir)
        self._panels: dict[str, tk.Frame] = {}
        self._build_shell()
        self._bind_events()
        self._show_panel("Control")
        self.after(50, self._initial_fetch)

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
        self._panels["Control"] = control
        self._panels["Metrics"] = PlaceholderPanel(self._workspace, "METRICS", "Metrics panel reserved for richer charts and control-home derivatives.")
        self._panels["Reports"] = PlaceholderPanel(self._workspace, "REPORTS", "Reports panel reserved for lineage, report bodies, and exports.")
        self._panels["Support"] = PlaceholderPanel(self._workspace, "SUPPORT", "Native GUI shell running against local CIEL-_SOT_Agent checkout.\n\nSet CIEL_SOT_AGENT_ROOT if the engine is not adjacent to this repo.")
        for panel in self._panels.values():
            panel.pack_forget()

    def _bind_events(self) -> None:
        bus.subscribe("nav:changed", self._on_nav)

    def _on_nav(self, name: str) -> None:
        self._show_panel(name)

    def _show_panel(self, name: str) -> None:
        for key, panel in self._panels.items():
            if key == name:
                panel.pack(fill=tk.BOTH, expand=True)
            else:
                panel.pack_forget()

    def _initial_fetch(self) -> None:
        self._data_service.refresh()
        self.after(REFRESH_MS, self._schedule_refresh)

    def _schedule_refresh(self) -> None:
        self._data_service.refresh()
        self.after(REFRESH_MS, self._schedule_refresh)


def main() -> None:
    app = CIELNativeGUI(Path.cwd())
    app.mainloop()


if __name__ == "__main__":
    main()
