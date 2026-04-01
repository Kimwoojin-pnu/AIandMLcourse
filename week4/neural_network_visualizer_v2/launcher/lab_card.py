from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QPainter, QColor
from shared.colors import COLORS


class LabCard(QFrame):
    open_requested = Signal(str)

    def __init__(self, meta: dict, parent=None):
        super().__init__(parent)
        self._meta = meta
        self.setObjectName("LabCard")
        self.setFixedSize(230, 188)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Base stylesheet — left accent border is the signature element
        self.setStyleSheet(f"""
            QFrame#LabCard {{
                background: {COLORS['panel']};
                border: 1px solid {COLORS['border']};
                border-left: 4px solid {COLORS['accent']};
                border-radius: 0px;
            }}
            QFrame#LabCard:hover {{
                background: {COLORS['card']};
                border: 1px solid {COLORS['border_light']};
                border-left: 4px solid {COLORS['accent']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 14, 14)
        layout.setSpacing(4)

        # Lab number — large, dim, decorative
        num_lbl = QLabel(meta.get("id", "").replace("lab", "").split("_")[0].upper())
        num_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 26pt; font-weight: 700; "
            f"font-family: Consolas, 'Courier New', monospace; "
            f"background: transparent; border: none; letter-spacing: 2px;"
        )
        layout.addWidget(num_lbl)

        # Title
        title = QLabel(meta["title"].upper())
        title.setStyleSheet(
            f"color: {COLORS['text']}; font-size: 8pt; font-weight: 700; "
            f"font-family: Consolas, 'Courier New', monospace; "
            f"background: transparent; border: none; letter-spacing: 1px;"
        )
        title.setWordWrap(True)
        layout.addWidget(title)

        # Description
        desc = QLabel(meta["description"])
        desc.setStyleSheet(
            f"color: {COLORS['text_dim']}; font-size: 8pt; "
            f"font-family: Consolas, 'Courier New', monospace; "
            f"background: transparent; border: none;"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        # Open button — amber on click
        btn = QPushButton("OPEN  →")
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['accent']};
                border: 1px solid {COLORS['accent']};
                border-radius: 0px;
                padding: 5px 10px;
                font-size: 8pt;
                font-weight: 700;
                font-family: Consolas, 'Courier New', monospace;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: {COLORS['accent']};
                color: {COLORS['bg']};
            }}
            QPushButton:pressed {{
                background: {COLORS['text']};
                color: {COLORS['bg']};
            }}
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.open_requested.emit(meta["window_class"]))
        layout.addWidget(btn)
