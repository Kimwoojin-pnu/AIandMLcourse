"""
CNN 합성곱 필터 시각화 프로그램 (PySide6)
────────────────────────────────────────────────────────
실행 방법 (VS Code 터미널):
    python main.py

의존성 설치 (최초 1회):
    pip install pyside6 pillow

기능:
  - PNG / JPG 이미지 업로드 → 자동 128×128 그레이스케일 변환
  - Sharpen / Edge Detect / Sobel X 필터 선택
  - Step(단계별) / Auto(자동 재생) / Reset
  - 합성곱 계산 과정 실시간 표시
────────────────────────────────────────────────────────
"""

import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from PySide6.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
