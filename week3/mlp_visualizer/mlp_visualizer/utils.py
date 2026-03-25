"""utils.py"""
import matplotlib
import matplotlib.font_manager as fm


def setup_korean_font() -> str:
    candidates = [
        "Malgun Gothic", "AppleGothic", "Apple SD Gothic Neo",
        "NanumGothic", "NanumBarunGothic", "Noto Sans CJK KR", "UnDotum",
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    chosen = next((c for c in candidates if c in available), None)
    if chosen:
        matplotlib.rcParams["font.family"] = chosen
    matplotlib.rcParams["axes.unicode_minus"] = False
    return chosen or "default"


import numpy as np
X_XOR = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
y_XOR = np.array([[0], [1], [1], [0]], dtype=float)
