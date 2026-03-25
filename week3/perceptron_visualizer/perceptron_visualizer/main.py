"""
main.py
퍼셉트론 학습 도구 — 진입점 (Entry Point)

실행 방법:
    python main.py

의존 패키지:
    pip install PySide6 numpy matplotlib
"""
import sys
import os

# ── 경로 설정: main.py 가 있는 디렉터리를 sys.path 에 추가 ──
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from main_window import MainWindow


def main():
    # 고DPI 지원
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("퍼셉트론 학습 도구")
    app.setApplicationVersion("1.0.0")
    app.setStyle("Fusion")   # 플랫폼 무관하게 일관된 UI

    # 기본 폰트 설정 (운영체제별)
    base_font = QFont()
    for family in ["Malgun Gothic", "Apple SD Gothic Neo", "NanumGothic"]:
        base_font.setFamily(family)
        break  # 첫 번째 후보 사용 (Qt가 폴백 처리)
    base_font.setPointSize(10)
    app.setFont(base_font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
