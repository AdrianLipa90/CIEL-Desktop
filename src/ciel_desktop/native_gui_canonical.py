from __future__ import annotations

from pathlib import Path

from .native_gui_shell_v2 import CIELNativeGUIV2


class CIELNativeGUICanonical(CIELNativeGUIV2):
    """
    Canonical native GUI entrypoint.

    This class currently reuses the richer v2 shell because v2 already contains
    the real Metrics and Reports panels. The older v1 shell remains available as
    an explicit compatibility/dev mode, but this module defines the preferred
    native GUI surface moving forward.
    """

    def __init__(self, root_dir: str | Path | None = None) -> None:
        super().__init__(root_dir)
        self.title("CIEL Desktop · Canonical Native GUI")


def main() -> None:
    app = CIELNativeGUICanonical(Path.cwd())
    app.mainloop()


if __name__ == "__main__":
    main()
