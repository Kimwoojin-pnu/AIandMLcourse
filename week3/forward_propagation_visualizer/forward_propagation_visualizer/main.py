"""main.py — 진입점"""
import sys
import matplotlib
matplotlib.use("QtAgg")

from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from utils import setup_korean_font


def main():
    setup_korean_font()
    app = QApplication(sys.argv)
    app.setApplicationName("순전파 학습 도구")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
