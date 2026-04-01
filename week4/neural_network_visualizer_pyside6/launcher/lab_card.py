from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal
from shared.colors import COLORS


class LabCard(QFrame):
    open_requested = Signal(str)   # emits window_class path

    def __init__(self, meta: dict, parent=None):
        super().__init__(parent)
        self._meta = meta
        self.setObjectName("LabCard")
        self.setFixedSize(200, 170)
        self.setStyleSheet(f"""
            QFrame#LabCard {{
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QFrame#LabCard:hover {{
                border: 1px solid {COLORS['accent']};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(4)

        icon = QLabel(meta["icon"])
        icon.setStyleSheet(f"font-size: 28px; background: transparent; border: none;")
        layout.addWidget(icon)

        title = QLabel(meta["title"])
        title.setStyleSheet(f"color: {COLORS['text']}; font-weight: bold; font-size: 12px; background: transparent; border: none;")
        title.setWordWrap(True)
        layout.addWidget(title)

        desc = QLabel(meta["description"])
        desc.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; background: transparent; border: none;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        btn = QPushButton("열기")
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']}; color: {COLORS['bg']};
                border: none; border-radius: 4px;
                padding: 5px; font-size: 11px; font-weight: bold;
            }}
        """)
        btn.clicked.connect(lambda: self.open_requested.emit(meta["window_class"]))
        layout.addWidget(btn)
