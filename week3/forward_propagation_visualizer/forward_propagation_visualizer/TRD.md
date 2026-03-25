# TRD — 순전파 학습 도구 (Forward Propagation Visualizer)

> **버전:** 1.0.0
> **기술 스택:** Python 3.10+ / PySide6 / NumPy / Matplotlib

---

## 1. 기술 스택

| 계층 | 라이브러리 | 버전 | 역할 |
|------|-----------|------|------|
| GUI 프레임워크 | PySide6 (Qt6) | ≥ 6.5 | 위젯, 레이아웃, 이벤트 루프 |
| 수치 계산 | NumPy | ≥ 1.24 | 행렬 연산 |
| 시각화 | Matplotlib | ≥ 3.7 | 뉴런 다이어그램, 히트맵, 막대 차트 |
| Matplotlib 백엔드 | `backend_qtagg` | 내장 | Qt 캔버스 임베드 |

---

## 2. 프로젝트 파일 구조

```
forward_propagation_visualizer/
├── main.py
├── main_window.py
├── theory_widget.py
├── explorer_widget.py       # 순전파 탐색 (슬라이더 + 뉴런 다이어그램)
├── matrix_widget.py         # 행렬 시각화 (히트맵)
├── network_model.py         # SimpleNetwork 순수 로직
├── styles.py
├── utils.py
└── requirements.txt
```

---

## 3. 모듈별 상세 명세

### 3.1 `network_model.py` — SimpleNetwork

```
SimpleNetwork
├── __init__(seed=42)
│     W1: np.ndarray (2,3) ← randn * 0.5
│     b1: np.ndarray (3,)  ← randn * 0.1
│     W2: np.ndarray (3,1) ← randn * 0.5
│     b2: np.ndarray (1,)  ← randn * 0.1
│
├── randomize(seed=None)
│     가중치 재무작위 초기화
│
└── forward(x1, x2) → ForwardResult
      z1 = W1.T @ [x1,x2] + b1  → (3,)
      a1 = relu(z1)               → (3,)
      z2 = W2.T @ a1 + b2         → scalar
      a2 = sigmoid(z2)            → scalar
      return ForwardResult(z1, a1, z2, a2)

ForwardResult (dataclass):
  z1: np.ndarray  # (3,) before ReLU
  a1: np.ndarray  # (3,) after ReLU
  z2: float       # before Sigmoid
  a2: float       # after Sigmoid (output)
```

### 3.2 `explorer_widget.py` — ExplorerWidget

#### 레이아웃
```
QWidget
└── QHBoxLayout
    ├── 좌 패널 (width=260)
    │   ├── QGroupBox "입력값"
    │   │   ├── x1 QSlider (−300~+300 → /100) + QLabel
    │   │   └── x2 QSlider (−300~+300 → /100) + QLabel
    │   ├── QPushButton "가중치 무작위"
    │   ├── QCheckBox "Seed 고정 (42)"
    │   └── QGroupBox "출력 결과"
    │       ├── QLabel "a₂ = 0.xxxx"  (크게 표시)
    │       ├── QLabel "z₂ = 0.xxxx"
    │       └── 3× QLabel "h₁/h₂/h₃ = 0.xx"
    └── 우 캔버스 (FigureCanvas)
        fig (1×2):
          ax[0]: 뉴런 다이어그램 (circles + edges + values)
          ax[1]: z1 vs a1 막대 비교
```

#### 뉴런 다이어그램 렌더링
```
ax.clear()

# 뉴런 위치 (x, y)
input_pos  = [(0.1, 0.3), (0.1, 0.7)]           # x1, x2
hidden_pos = [(0.5, 0.15),(0.5, 0.5),(0.5, 0.85)] # h1, h2, h3
output_pos = [(0.9, 0.5)]                          # y

# 색상: 활성화 강도 → RdYlGn colormap (0~1 정규화)
# 연결선: alpha = abs(weight) / max_weight

for pos, val in zip(hidden_pos, a1):
    color = cmap(normalize(val))
    circle = plt.Circle(pos, 0.06, color=color)
    ax.add_patch(circle)
    ax.text(pos[0], pos[1], f"{val:.2f}", ha='center', va='center')
```

### 3.3 `matrix_widget.py` — MatrixWidget

#### 레이아웃
```
QWidget
└── QVBoxLayout
    ├── QPushButton "가중치 무작위"
    └── FigureCanvas
        fig (2×2):
          ax[0,0]: W1 (2×3) imshow heatmap + 값 텍스트
          ax[0,1]: W2 (3×1) imshow heatmap + 값 텍스트
          ax[1,0]: z1 vs a1 막대 비교 (grouped bar)
          ax[1,1]: z2 / a2 수평 막대
```

---

## 4. 데이터 흐름

```
슬라이더 이동 / 무작위 버튼
    → network.forward(x1, x2) → ForwardResult
    → ExplorerWidget._draw(result)
         → 뉴런 다이어그램 업데이트
         → 막대 차트 업데이트
         → 출력 라벨 업데이트
    → MatrixWidget._draw()  ← 가중치 변경 시만
         → W1, W2 히트맵 업데이트
```

---

## 5. 성능 고려사항

| 항목 | 설계 결정 |
|------|-----------|
| 다이어그램 해상도 | 원 반경 0.06 (논리 좌표) |
| 모델 공유 | ExplorerWidget·MatrixWidget이 동일 `network` 인스턴스 참조 |

---

*문서 끝*
