from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter.scrolledtext import ScrolledText

from .config import APP_GEOMETRY, APP_TITLE, COLORS, FONTS, ROOT_DIR
from .core.operator_actions import run_operator_action
from .core.sot_adapter import build_orbital_bridge, build_panel_state, build_sync_report, resolve_sot_root


class CIELDesktopApp(tk.Tk):
    def __init__(self, sot_root: str | Path | None = None) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.configure(bg=COLORS["bg"])
        self.minsize(1180, 760)
        self._sot_root = resolve_sot_root(sot_root)
        self._build_ui()
        self._refresh_state()

    def _build_ui(self) -> None:
        top = tk.Frame(self, bg=COLORS["bg_panel"], height=42)
        top.pack(side=tk.TOP, fill=tk.X)
        top.pack_propagate(False)
        tk.Label(top, text="CIEL DESKTOP", font=FONTS["title"], bg=COLORS["bg_panel"], fg=COLORS["cyan"]).pack(side=tk.LEFT, padx=12)
        self.status_var = tk.StringVar(value="connecting")
        tk.Label(top, textvariable=self.status_var, font=FONTS["mono_sm"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(side=tk.RIGHT, padx=12)

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(body, bg=COLORS["bg_panel"], width=240)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
        left.pack_propagate(False)
        tk.Label(left, text="CONTROL", font=FONTS["title"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(anchor="w", padx=12, pady=(12, 6))
        for action_key, label in [
            ("refresh", "refresh state"),
            ("run_sync", "run sync"),
            ("run_orbital", "run orbital"),
            ("rebuild_packet", "rebuild packet"),
            ("operator_cycle", "operator cycle"),
        ]:
            tk.Button(
                left,
                text=label,
                font=FONTS["mono_sm"],
                bg=COLORS["bg_input"],
                fg=COLORS["cyan"],
                relief=tk.FLAT,
                command=lambda k=action_key: self._handle_action(k),
            ).pack(fill=tk.X, padx=12, pady=3)

        center = tk.Frame(body, bg=COLORS["bg"])
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        metrics = tk.Frame(center, bg=COLORS["bg"])
        metrics.pack(fill=tk.X, padx=12, pady=12)
        self.metric_labels = {}
        for key in ["coherence", "defect", "energy", "mode"]:
            box = tk.Frame(metrics, bg=COLORS["bg_panel"], padx=10, pady=8)
            box.pack(side=tk.LEFT, padx=(0, 10))
            tk.Label(box, text=key, font=FONTS["mono_sm"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(anchor="w")
            var = tk.StringVar(value="—")
            tk.Label(box, textvariable=var, font=FONTS["mono_lg"], bg=COLORS["bg_panel"], fg=COLORS["cyan"]).pack(anchor="w")
            self.metric_labels[key] = var

        self.log = ScrolledText(center, font=FONTS["mono_sm"], bg=COLORS["bg_panel"], fg=COLORS["text"], relief=tk.FLAT)
        self.log.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        right = tk.Frame(body, bg=COLORS["bg_panel"], width=340)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)
        tk.Label(right, text="FOCUS / PROVENANCE", font=FONTS["title"], bg=COLORS["bg_panel"], fg=COLORS["text_dim"]).pack(anchor="w", padx=12, pady=(12, 6))
        self.focus = ScrolledText(right, font=FONTS["mono_sm"], bg=COLORS["bg_panel"], fg=COLORS["text"], relief=tk.FLAT)
        self.focus.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

    def _append_log(self, text: str) -> None:
        self.log.insert("1.0", text + "\n")

    def _set_focus(self, text: str) -> None:
        self.focus.delete("1.0", tk.END)
        self.focus.insert("1.0", text)

    def _refresh_state(self) -> None:
        sync = build_sync_report(self._sot_root)
        bridge = build_orbital_bridge(self._sot_root)
        panel = build_panel_state(self._sot_root, user_text="Desktop bootstrap", sapiens_id="desktop")
        coherence = bridge.get("state_manifest", {}).get("coherence", bridge.get("health_manifest", {}).get("system_health", 0.0))
        defect = sync.get("closure_defect", 0.0)
        energy = bridge.get("health_manifest", {}).get("energy_budget", bridge.get("health_manifest", {}).get("system_health", 0.0))
        mode = bridge.get("recommended_control", {}).get("mode", "unknown")
        self.metric_labels["coherence"].set(str(coherence))
        self.metric_labels["defect"].set(str(defect))
        self.metric_labels["energy"].set(str(energy))
        self.metric_labels["mode"].set(str(mode))
        self.status_var.set(f"sot: {self._sot_root}")
        self._set_focus(
            f"mode: {mode}\n"
            f"closure_defect: {defect}\n"
            f"recommended_action: {bridge.get('health_manifest', {}).get('recommended_action', '—')}\n"
            f"session_id: {panel.get('session_id', '—')}\n"
        )
        self._append_log(f"refresh -> coherence={coherence} defect={defect} mode={mode}")

    def _handle_action(self, action_key: str) -> None:
        if action_key == "refresh":
            self._refresh_state()
            return
        result = run_operator_action(self._sot_root, action_key)
        self._append_log(f"{result.get('ts', '—')}  {result.get('label', action_key)}  {result.get('details', '—')}")
        self._refresh_state()


def main() -> None:
    app = CIELDesktopApp(ROOT_DIR)
    app.mainloop()


if __name__ == "__main__":
    main()
