from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Callable

from .main import main as run_bootstrap
from .native_gui_shell import main as run_v1
from .native_gui_shell_v2 import main as run_v2


class LauncherHub(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CIEL Desktop Launcher Hub")
        self.geometry("560x320")
        self.configure(bg="#0e0e0e")
        self.resizable(False, False)
        self._build()

    def _build(self) -> None:
        wrap = tk.Frame(self, bg="#0e0e0e")
        wrap.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            wrap,
            text="CIEL DESKTOP",
            font=("Courier New", 14, "bold"),
            bg="#0e0e0e",
            fg="#00c0c0",
        ).pack(anchor="w")

        tk.Label(
            wrap,
            text="Unified launcher for desktop shell modes",
            font=("Courier New", 9),
            bg="#0e0e0e",
            fg="#8a8a8a",
        ).pack(anchor="w", pady=(2, 16))

        self._mode_row(
            wrap,
            "Bootstrap",
            "Stable minimal desktop shell already present on main.",
            run_bootstrap,
        )
        self._mode_row(
            wrap,
            "Native GUI v1",
            "Componentized control-home style shell from PR #2.",
            run_v1,
        )
        self._mode_row(
            wrap,
            "Native GUI v2",
            "Richer shell with Metrics and Reports panels.",
            run_v2,
        )

        note = (
            "All modes consume the local CIEL-_SOT_Agent checkout through the desktop adapter layer.\n"
            "Set CIEL_SOT_AGENT_ROOT when the engine is not adjacent to this repo."
        )
        tk.Label(
            wrap,
            text=note,
            justify=tk.LEFT,
            font=("Courier New", 8),
            bg="#0e0e0e",
            fg="#6a6a6a",
        ).pack(anchor="w", pady=(18, 0))

    def _mode_row(self, parent: tk.Misc, title: str, description: str, runner: Callable[[], None]) -> None:
        row = tk.Frame(parent, bg="#141414")
        row.pack(fill=tk.X, pady=4)

        text_col = tk.Frame(row, bg="#141414")
        text_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(
            text_col,
            text=title,
            font=("Courier New", 11, "bold"),
            bg="#141414",
            fg="#c8c8c8",
        ).pack(anchor="w")
        tk.Label(
            text_col,
            text=description,
            font=("Courier New", 8),
            bg="#141414",
            fg="#8a8a8a",
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(2, 0))

        tk.Button(
            row,
            text="launch",
            font=("Courier New", 9),
            bg="#1a1a1a",
            fg="#00c0c0",
            relief=tk.FLAT,
            padx=10,
            pady=6,
            command=lambda r=runner: self._launch(r),
        ).pack(side=tk.RIGHT, padx=10)

    def _launch(self, runner: Callable[[], None]) -> None:
        try:
            self.destroy()
            runner()
        except Exception as exc:
            messagebox.showerror("CIEL Desktop Launcher Hub", str(exc))


def main() -> None:
    app = LauncherHub()
    app.mainloop()


if __name__ == "__main__":
    main()
