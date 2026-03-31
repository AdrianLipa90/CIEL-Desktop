from __future__ import annotations

from pathlib import Path

APP_TITLE = "CIEL Desktop"
APP_GEOMETRY = "1480x900"
ROOT_DIR = Path(__file__).resolve().parents[2]
SOT_AGENT_ENV = "CIEL_SOT_AGENT_ROOT"

COLORS = {
    "bg": "#0e0e0e",
    "bg_panel": "#141414",
    "bg_input": "#1a1a1a",
    "border": "#242424",
    "text": "#c8c8c8",
    "text_dim": "#6a6a6a",
    "cyan": "#00c0c0",
    "amber": "#c89000",
    "red": "#c03030",
    "violet": "#7040a0",
    "green": "#408050",
}

FONTS = {
    "mono": ("Courier New", 10),
    "mono_sm": ("Courier New", 9),
    "mono_lg": ("Courier New", 12, "bold"),
    "title": ("Courier New", 10, "bold"),
}
