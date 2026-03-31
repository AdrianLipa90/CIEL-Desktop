from __future__ import annotations

import importlib


MODULES = [
    "ciel_desktop.main",
    "ciel_desktop.native_gui_shell",
    "ciel_desktop.native_gui_shell_v2",
    "ciel_desktop.native_gui_canonical",
    "ciel_desktop.launcher_hub",
]


def test_desktop_modules_import() -> None:
    for module_name in MODULES:
        module = importlib.import_module(module_name)
        assert module is not None


def test_main_entrypoints_exist() -> None:
    for module_name in MODULES:
        module = importlib.import_module(module_name)
        assert hasattr(module, "main")
        assert callable(module.main)
