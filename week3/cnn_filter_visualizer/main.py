"""
CNN 합성곱 필터 시각화 프로그램
────────────────────────────────────────────────────────
실행 방법 (VS Code 터미널):
    python main.py

의존성 설치 (최초 1회):
    pip install pillow

기능:
  - 8×8 픽셀 그리드 직접 입력
  - PNG / JPG 이미지 업로드 → 자동 8×8 그레이스케일 변환
  - Sharpen / Edge Detect / Sobel X 필터 선택
  - Step(단계별) / Auto(자동 재생) / Reset
  - 합성곱 계산 과정 실시간 표시
────────────────────────────────────────────────────────
"""

import sys
import os

# 프로젝트 루트를 sys.path에 추가 (어디서 실행해도 동작하도록)
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
