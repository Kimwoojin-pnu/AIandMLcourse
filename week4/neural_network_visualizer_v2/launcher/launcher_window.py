import sys
import glob
import importlib
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QLabel,
    QHBoxLayout, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPainter, QColor, QLinearGradient
from shared.colors import COLORS
from .lab_card import LabCard


def discover_labs() -> list[dict]:
    base = os.path.join(os.path.dirname(__file__), "..", "labs")
    pattern = os.path.join(base, "lab*", "lab_meta.py")
    metas = []
    for path in sorted(glob.glob(pattern)):
        parts = path.replace("\\", "/").split("/")
        lab_dir = parts[-2]
        module_name = f"labs.{lab_dir}.lab_meta"
        mod = importlib.import_module(module_name)
        metas.append(mod.LAB_META)
    return metas


class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Week 4 · Neural Network Visualizer")
        self.setMinimumSize(560, 540)
        self._open_windows: dict[str, object] = {}
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"QMainWindow, QWidget {{ background: {COLORS['bg']}; }}")
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Header ────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(68)
        header.setStyleSheet(
            f"background: {COLORS['panel']};"
            f"border-bottom: 2px solid {COLORS['accent']};"
        )
        hh = QHBoxLayout(header)
        hh.setContentsMargins(24, 0, 24, 0)
        hh.setSpacing(0)

        left_col = QVBoxLayout()
        left_col.setSpacing(2)
        title = QLabel("NEURAL NETWORK VISUALIZER")
        title.setStyleSheet(
            f"color: {COLORS['accent']}; font-size: 13pt; font-weight: 700; "
            f"font-family: Consolas, 'Courier New', monospace; "
            f"letter-spacing: 3px; background: transparent;"
        )
        left_col.addWidget(title)
        sub = QLabel("MIT 6.S191  ·  WEEK 4  ·  TENSORFLOW / PYSIDE6")
        sub.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 7pt; "
            f"font-family: Consolas, 'Courier New', monospace; "
            f"letter-spacing: 1px; background: transparent;"
        )
        left_col.addWidget(sub)
        hh.addLayout(left_col)
        hh.addStretch()

        # Decorative accent lines (right side of header)
        lines_widget = _AccentLines()
        lines_widget.setFixedSize(80, 40)
        hh.addWidget(lines_widget)

        root.addWidget(header)

        # ── Intro bar ─────────────────────────────────────────────────
        intro = QLabel("SELECT A LAB TO BEGIN")
        intro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        intro.setFixedHeight(28)
        intro.setStyleSheet(
            f"background: {COLORS['bg']}; color: {COLORS['text_muted']}; "
            f"font-size: 7pt; font-family: Consolas, 'Courier New', monospace; "
            f"letter-spacing: 3px; border-bottom: 1px solid {COLORS['border']};"
        )
        root.addWidget(intro)

        # ── Card grid ─────────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet(f"background: {COLORS['bg']};")
        grid = QGridLayout(body)
        grid.setContentsMargins(24, 20, 24, 20)
        grid.setSpacing(16)
        root.addWidget(body, stretch=1)

        metas = discover_labs()
        for i, meta in enumerate(metas):
            card = LabCard(meta)
            card.open_requested.connect(self._open_lab)
            grid.addWidget(card, i // 2, i % 2)

        # ── Footer ────────────────────────────────────────────────────
        footer = QLabel("PYSIDE6  ·  TENSORFLOW/KERAS  ·  MATPLOTLIB  ·  MIT 6.S191")
        footer.setFixedHeight(26)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            f"background: {COLORS['panel']}; color: {COLORS['text_muted']}; "
            f"font-size: 7pt; font-family: Consolas, 'Courier New', monospace; "
            f"letter-spacing: 1px; border-top: 1px solid {COLORS['border']};"
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


class _AccentLines(QWidget):
    """Small decorative widget: 4 horizontal amber lines of varying width."""
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QColor(COLORS["accent"])
        widths = [80, 52, 66, 38]
        for i, w in enumerate(widths):
            alpha = 200 - i * 35
            c.setAlpha(alpha)
            p.setPen(c)
            from PySide6.QtGui import QPen
            pen = p.pen()
            pen.setWidth(2)
            p.setPen(pen)
            y = 8 + i * 9
            p.drawLine(self.width() - w, y, self.width(), y)
        p.end()
