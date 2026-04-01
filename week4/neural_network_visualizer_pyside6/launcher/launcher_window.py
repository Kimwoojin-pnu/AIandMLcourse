import sys
import glob
import importlib
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QLabel,
    QHBoxLayout, QGraphicsOpacityEffect,
)
from PySide6.QtCore import QByteArray
from PySide6.QtSvgWidgets import QSvgWidget
from shared.colors import COLORS, CAT_SVG
from .lab_card import LabCard


def discover_labs() -> list[dict]:
    """Scan labs/lab*/lab_meta.py and return list of LAB_META dicts, sorted by id."""
    base = os.path.join(os.path.dirname(__file__), "..", "labs")
    pattern = os.path.join(base, "lab*", "lab_meta.py")
    metas = []
    for path in sorted(glob.glob(pattern)):
        parts = path.replace("\\", "/").split("/")
        lab_dir = parts[-2]           # e.g. "lab1_function"
        module_name = f"labs.{lab_dir}.lab_meta"
        mod = importlib.import_module(module_name)
        metas.append(mod.LAB_META)
    return metas


class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Week 4 · Neural Network Visualizer")
        self.setMinimumSize(520, 460)
        self._open_windows: dict[str, object] = {}
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"QMainWindow, QWidget {{ background: {COLORS['bg']}; }}")
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QWidget()
        header.setStyleSheet(f"background: {COLORS['panel']}; border-bottom: 1px solid {COLORS['border']};")
        hh = QHBoxLayout(header)
        hh.setContentsMargins(16, 10, 16, 10)
        title = QLabel("Week 4 · Neural Network Visualizer  |  MIT 6.S191")
        title.setStyleSheet(f"color: {COLORS['accent']}; font-size: 14px; font-weight: bold; background: transparent;")
        hh.addWidget(title)
        hh.addStretch()
        cat = QSvgWidget()
        cat.load(QByteArray(CAT_SVG))
        cat.setFixedSize(36, 36)
        cat.setStyleSheet("background: transparent;")
        fx = QGraphicsOpacityEffect(cat)
        fx.setOpacity(0.85)
        cat.setGraphicsEffect(fx)
        hh.addWidget(cat)
        root.addWidget(header)

        # Card grid
        body = QWidget()
        body.setStyleSheet(f"background: {COLORS['bg']};")
        grid = QGridLayout(body)
        grid.setContentsMargins(20, 20, 20, 20)
        grid.setSpacing(14)
        root.addWidget(body, stretch=1)

        metas = discover_labs()
        for i, meta in enumerate(metas):
            card = LabCard(meta)
            card.open_requested.connect(self._open_lab)
            grid.addWidget(card, i // 2, i % 2)

        # Footer
        footer = QLabel("PySide6 · TensorFlow/Keras · MIT 6.S191 Week 4")
        footer.setStyleSheet(
            f"background: {COLORS['panel']}; color: {COLORS['text_muted']}; "
            f"font-size: 10px; padding: 5px 16px; border-top: 1px solid {COLORS['border']};"
        )
        root.addWidget(footer)

    def _open_lab(self, window_class_path: str):
        if window_class_path in self._open_windows:
            w = self._open_windows[window_class_path]
            w.raise_()
            w.activateWindow()
            return
        try:
            module_path, cls_name = window_class_path.rsplit(".", 1)
            mod = importlib.import_module(module_path)
            cls = getattr(mod, cls_name)
            win = cls()
            from PySide6.QtCore import Qt
            win.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            win.destroyed.connect(lambda: self._open_windows.pop(window_class_path, None))
            self._open_windows[window_class_path] = win
            win.show()
        except Exception as exc:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Lab 열기 실패:\n{exc}")
