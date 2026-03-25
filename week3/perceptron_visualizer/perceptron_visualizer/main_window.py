"""
main_window.py
메인 윈도우 — 탭 위젯으로 세 탭을 조합
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QTabWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from theory_widget     import TheoryWidget
from simulation_widget import SimulationWidget
from manual_widget     import ManualWidget
from styles            import APP_STYLE


class MainWindow(QMainWindow):
    """퍼셉트론 학습 도구 메인 윈도우"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("퍼셉트론 학습 도구 — Perceptron Visualizer")
        self.setMinimumSize(1240, 780)
        self.resize(1340, 840)

        self._build_ui()
        self.setStyleSheet(APP_STYLE + self._tab_style())

    # ─────────────────────────────────────────
    # UI 구성
    # ─────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        # 탭 위젯
        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)

        self._theory_w     = TheoryWidget()
        self._simulation_w = SimulationWidget()
        self._manual_w     = ManualWidget()

        self._tabs.addTab(self._theory_w,     "  📖  이론 설명  ")
        self._tabs.addTab(self._simulation_w, "  🔬  학습 시뮬레이션  ")
        self._tabs.addTab(self._manual_w,     "  🎛️  직접 조작  ")

        root.addWidget(self._tabs)
        root.addWidget(self._build_footer())

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(58)
        header.setStyleSheet("background: #1a2634;")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("🧠  퍼셉트론 학습 도구")
        logo.setStyleSheet(
            "color: white; font-size: 17px; font-weight: bold;"
        )
        sub = QLabel("Perceptron Visualizer  |  신경망 기초 학습 도구")
        sub.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        sub.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(logo)
        layout.addStretch()
        layout.addWidget(sub)
        return header

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        footer.setFixedHeight(28)
        footer.setStyleSheet("background: #f0f4f8; border-top: 1px solid #dee2e6;")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(16, 0, 16, 0)

        tips = [
            "💡 이론 탭에서 개념을 이해한 후",
            "→  시뮬레이션 탭에서 AND·OR·XOR 학습 과정을 확인하고",
            "→  직접 조작 탭에서 가중치를 바꾸며 결정 경계를 탐색해보세요!",
        ]
        tip_lbl = QLabel("   ".join(tips))
        tip_lbl.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        layout.addWidget(tip_lbl)
        return footer

    # ─────────────────────────────────────────
    # 탭 스타일
    # ─────────────────────────────────────────
    @staticmethod
    def _tab_style() -> str:
        return """
            QTabWidget::pane {
                border: none;
                border-top: 1px solid #dee2e6;
                background: #f4f6f8;
            }
            QTabBar {
                background: #f0f4f8;
            }
            QTabBar::tab {
                background: #f0f4f8;
                color: #6c757d;
                padding: 11px 22px;
                font-size: 13px;
                border: none;
                border-right: 1px solid #dee2e6;
            }
            QTabBar::tab:selected {
                background: white;
                color: #2980b9;
                font-weight: bold;
                border-top: 3px solid #2980b9;
            }
            QTabBar::tab:hover:!selected {
                background: #e8edf2;
                color: #2c3e50;
            }
        """
