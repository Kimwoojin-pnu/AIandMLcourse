"""
styles.py
앱 전체에서 공유하는 Qt 스타일시트 상수
"""

# ── 그룹박스 ──────────────────────────────────────
GROUP_STYLE = """
    QGroupBox {
        font-weight: bold;
        font-size: 12px;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 14px;
        background: white;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 5px;
        color: #2c3e50;
    }
"""

# ── 버튼 ──────────────────────────────────────────
PRIMARY_BTN = """
    QPushButton {
        background: #2980b9;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 18px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton:hover   { background: #3498db; }
    QPushButton:pressed { background: #1f6fa3; }
    QPushButton:disabled { background: #bdc3c7; color: #7f8c8d; }
"""

SECONDARY_BTN = """
    QPushButton {
        background: #ecf0f1;
        color: #2c3e50;
        border: 1px solid #bdc3c7;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 13px;
    }
    QPushButton:hover   { background: #dfe6e9; }
    QPushButton:pressed { background: #ccd4d7; }
"""

PAUSE_BTN = """
    QPushButton {
        background: #e67e22;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 18px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton:hover   { background: #f39c12; }
    QPushButton:pressed { background: #ca6f1e; }
"""

SUCCESS_BTN = """
    QPushButton {
        background: #27ae60;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton:hover   { background: #2ecc71; }
"""

# ── 테이블 ────────────────────────────────────────
TABLE_STYLE = """
    QTableWidget {
        font-size: 12px;
        gridline-color: #dee2e6;
        border: 1px solid #dee2e6;
        border-radius: 4px;
    }
    QHeaderView::section {
        background: #2980b9;
        color: white;
        padding: 5px 8px;
        font-weight: bold;
        border: none;
    }
    QTableWidget::item { padding: 4px 8px; }
    QTableWidget::item:selected { background: #d6eaf8; color: #2c3e50; }
"""

# ── 슬라이더 ──────────────────────────────────────
SLIDER_STYLE = """
    QSlider::groove:horizontal {
        height: 6px;
        background: #dee2e6;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        width: 16px;
        height: 16px;
        background: #2980b9;
        border-radius: 8px;
        margin: -5px 0;
    }
    QSlider::handle:horizontal:hover { background: #3498db; }
    QSlider::sub-page:horizontal {
        background: #2980b9;
        border-radius: 3px;
    }
"""

# ── 라디오 버튼 ───────────────────────────────────
RADIO_STYLE = """
    QRadioButton {
        font-size: 13px;
        padding: 4px 2px;
        color: #2c3e50;
    }
    QRadioButton::indicator { width: 16px; height: 16px; }
    QRadioButton::indicator:checked {
        background: #2980b9;
        border: 2px solid #2980b9;
        border-radius: 8px;
    }
    QRadioButton::indicator:unchecked {
        background: white;
        border: 2px solid #bdc3c7;
        border-radius: 8px;
    }
"""

# ── 앱 전역 스타일 ────────────────────────────────
APP_STYLE = """
    * {
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo',
                     'NanumGothic', 'Noto Sans CJK KR', sans-serif;
    }
    QMainWindow { background: #f4f6f8; }
    QWidget     { background: #f4f6f8; }
    QScrollArea { background: white; border: none; }
    QScrollBar:vertical {
        width: 8px; background: transparent;
    }
    QScrollBar::handle:vertical {
        background: #bdc3c7; border-radius: 4px;
    }
    QSpinBox, QDoubleSpinBox {
        border: 1px solid #bdc3c7;
        border-radius: 4px;
        padding: 4px 6px;
        font-size: 12px;
    }
"""
