import sys
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Ensure the package root is on the path when running as a script
sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from launcher.launcher_window import LauncherWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Week4 NN Visualizer")
    win = LauncherWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
