"""main_window.py — 메인 윈도우"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
)
from PySide6.QtCore import Qt

from theory_widget import TheoryWidget
from explorer_widget import ExplorerWidget
from comparison_widget import ComparisonWidget
from styles import APP_STYLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("활성화 함수 학습 도구 v1.0")
        self.setMinimumSize(1240, 780)
        self.setStyleSheet(APP_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── 헤더 ──────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(58)
        header.setStyleSheet("background: #1a2634;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("⚡ 활성화 함수 학습 도구")
        logo.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        subtitle = QLabel("Activation Functions Visualizer — Week 3")
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 12px;")

        hl.addWidget(logo)
        hl.addStretch()
        hl.addWidget(subtitle)
        root.addWidget(header)

        # ── 탭 ────────────────────────────────────────
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #f4f6f8; }
            QTabBar::tab {
                padding: 10px 24px; font-size: 13px; font-weight: bold;
                background: #dfe6e9; color: #636e72; border: none;
                border-bottom: 3px solid transparent;
            }
            QTabBar::tab:selected { background: white; color: #2980b9; border-bottom: 3px solid #2980b9; }
            QTabBar::tab:hover    { background: #ecf0f1; }
        """)

        tabs.addTab(TheoryWidget(),    "📖 이론 설명")
        tabs.addTab(ExplorerWidget(),  "🔍 함수 탐색")
        tabs.addTab(ComparisonWidget(),"📊 비교")
        root.addWidget(tabs, 1)

        # ── 푸터 ──────────────────────────────────────
        footer = QWidget()
        footer.setFixedHeight(28)
        footer.setStyleSheet("background: #f0f4f8;")
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(16, 0, 16, 0)
        fl.addWidget(QLabel("학습 순서: 이론 설명 → 함수 탐색 → 비교"))
        fl.addStretch()
        fl.addWidget(QLabel("Week 3 — 활성화 함수"))
        root.addWidget(footer)
