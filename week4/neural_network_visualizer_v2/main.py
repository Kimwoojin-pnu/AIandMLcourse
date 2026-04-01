import sys
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from launcher.launcher_window import LauncherWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Week4 NN Visualizer v2")

    # Set default application font
    f = QFont("Consolas")
    if not f.exactMatch():
        f = QFont("Courier New")
    f.setPointSize(9)
    app.setFont(f)

    win = LauncherWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
