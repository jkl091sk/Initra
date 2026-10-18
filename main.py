from pathlib import Path
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.styles.theme import APP_STYLE
from app.views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Initra")
    app.setDesktopFileName("initra")
    app.setWindowIcon(QIcon(str(Path(__file__).resolve().parent / "assets" / "initra_logo.png")))
    app.setOrganizationName("Initra")
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
