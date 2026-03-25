"""
utils.py
공통 유틸리티 함수
"""
import matplotlib
import matplotlib.font_manager as fm


# ── 한글 폰트 설정 ─────────────────────────────────
def setup_korean_font() -> str:
    """
    운영체제별 한글 폰트 자동 설정 후 설정된 폰트명 반환.
    매칭 폰트 없으면 기본 폰트 사용.
    """
    candidates = [
        "Malgun Gothic",      # Windows
        "AppleGothic",        # macOS (구)
        "Apple SD Gothic Neo",# macOS (신)
        "NanumGothic",        # Linux / 설치형
        "NanumBarunGothic",
        "Noto Sans CJK KR",   # Linux Google Noto
        "UnDotum",            # Linux 은글꼴
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    chosen = None
    for c in candidates:
        if c in available:
            chosen = c
            break

    if chosen:
        matplotlib.rcParams["font.family"] = chosen
    matplotlib.rcParams["axes.unicode_minus"] = False
    return chosen or "default"


# ── 논리 게이트 데이터 ──────────────────────────────
import numpy as np

X_DATA = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)

GATE_LABELS: dict[str, np.ndarray] = {
    "AND": np.array([0, 0, 0, 1]),
    "OR":  np.array([0, 1, 1, 1]),
    "XOR": np.array([0, 1, 1, 0]),
}

GATE_DESC = {
    "AND": "두 입력이 모두 1일 때만 출력 1  →  선형 분리 가능 ✓",
    "OR":  "하나 이상의 입력이 1이면 출력 1  →  선형 분리 가능 ✓",
    "XOR": "두 입력이 다를 때 출력 1  →  선형 분리 불가능 ✗",
}
