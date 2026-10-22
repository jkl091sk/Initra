from pathlib import Path
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.services.ui_animation_service import UiAnimationService
from app.services.v31_compat_service import V31CompatService
from app.styles.theme import APP_STYLE
from app.styles.v31_overrides import V31_STYLE
from app.views.main_window import MainWindow


# Install v3.1 workflow fixes before MainWindow is constructed so existing
# buttons/signals bind to the corrected distro-aware handlers.
V31CompatService.install(MainWindow)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Initra")
    app.setApplicationDisplayName("Initra")
    app.setApplicationVersion("3.1.0")
    app.setDesktopFileName("initra")
    app.setOrganizationName("Initra")

    icon_path = Path(__file__).resolve().parent / "assets" / "initra_logo.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # v3.1 overrides are intentionally last: old rules cannot restore the
    # section-tab pane line or the previous underline-style selection.
    app.setStyleSheet(APP_STYLE + "\n" + V31_STYLE)

    window = MainWindow()

    # v3.1 extends motion to startup and every section tab while respecting
    # Settings > Animations.
    window.ui_animations = UiAnimationService(window)
    window.ui_animations.install()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
