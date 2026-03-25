"""main.py"""
import sys
import matplotlib
matplotlib.use("QtAgg")
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from utils import setup_korean_font

def main():
    setup_korean_font()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
