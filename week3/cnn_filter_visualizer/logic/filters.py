FILTERS = {
    "Sharpen": {
        "kernel": [
            [ 0, -1,  0],
            [-1,  5, -1],
            [ 0, -1,  0],
        ],
        "mode": "clamp",
        "desc": "에지 강조, 균일 영역 유지",
    },
    "Edge Detect": {
        "kernel": [
            [0,  1, 0],
            [1, -4, 1],
            [0,  1, 0],
        ],
        "mode": "abs",
        "desc": "모든 방향 에지 검출 (Laplacian)",
    },
    "Sobel X": {
        "kernel": [
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1],
        ],
        "mode": "abs",
        "desc": "수직 에지 강조 (좌우 변화)",
    },
}

FILTER_NAMES = list(FILTERS.keys())
