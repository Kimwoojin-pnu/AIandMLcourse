# TRD — 활성화 함수 학습 도구 (Activation Functions Visualizer)

> **버전:** 1.0.0
> **기술 스택:** Python 3.10+ / PySide6 / NumPy / Matplotlib

---

## 1. 기술 스택

| 계층 | 라이브러리 | 버전 | 역할 |
|------|-----------|------|------|
| GUI 프레임워크 | PySide6 (Qt6) | ≥ 6.5 | 위젯, 레이아웃, 이벤트 루프 |
| 수치 계산 | NumPy | ≥ 1.24 | 활성화 함수 벡터 연산 |
| 시각화 | Matplotlib | ≥ 3.7 | 그래프 렌더링 (Qt 백엔드 embed) |
| Matplotlib 백엔드 | `backend_qtagg` | 내장 | Qt 캔버스에 Figure 임베드 |

---

## 2. 프로젝트 파일 구조

```
activation_functions_visualizer/
├── main.py                  # 진입점 (QApplication, MainWindow 시작)
├── main_window.py           # QMainWindow: 헤더 + QTabWidget + 푸터
├── theory_widget.py         # QWidget: 이론 설명 (QTextBrowser + HTML)
├── explorer_widget.py       # QWidget: 함수 탐색 (슬라이더 + 실시간 플롯)
├── comparison_widget.py     # QWidget: 함수 비교 (체크박스 + 오버레이 플롯)
├── activation_model.py      # 활성화 함수 순수 로직 (비-GUI)
├── styles.py                # Qt 스타일시트 상수
├── utils.py                 # 한글 폰트 설정
└── requirements.txt
```

---

## 3. 모듈별 상세 명세

### 3.1 `activation_model.py`

```
함수 목록:
  sigmoid(x)           → 1 / (1 + exp(-x))
  sigmoid_deriv(x)     → sigmoid(x) * (1 - sigmoid(x))
  tanh_fn(x)           → np.tanh(x)
  tanh_deriv(x)        → 1 - tanh(x)²
  relu(x)              → np.maximum(0, x)
  relu_deriv(x)        → np.where(x > 0, 1, 0)
  leaky_relu(x, alpha) → np.where(x > 0, x, alpha * x)
  leaky_relu_deriv(x, alpha) → np.where(x > 0, 1, alpha)

FUNC_MAP: dict[str, tuple[callable, callable]]
  "Sigmoid" → (sigmoid, sigmoid_deriv)
  "Tanh"    → (tanh_fn, tanh_deriv)
  "ReLU"    → (relu, relu_deriv)
  "Leaky ReLU" → (leaky_relu, leaky_relu_deriv)  ← alpha 별도 처리

COLORS: dict[str, str]
  "Sigmoid"    → "#e74c3c"
  "Tanh"       → "#3498db"
  "ReLU"       → "#2ecc71"
  "Leaky ReLU" → "#f39c12"
```

### 3.2 `explorer_widget.py` — ExplorerWidget

#### 레이아웃
```
QWidget (ExplorerWidget)
└── QHBoxLayout
    ├── 좌 패널 (QWidget, width=280)
    │   ├── QGroupBox "함수 선택"
    │   │   └── 4× QRadioButton (Sigmoid/Tanh/ReLU/Leaky ReLU)
    │   ├── QGroupBox "x 값"
    │   │   ├── QSlider (−600 ~ +600 → /100.0)
    │   │   └── QLabel (현재 x 값)
    │   ├── QGroupBox "Leaky α"  ← Leaky ReLU 선택 시만 활성
    │   │   ├── QSlider (1 ~ 50 → /100.0)
    │   │   └── QLabel (현재 α 값)
    │   ├── QCheckBox "접선 표시"
    │   └── QGroupBox "현재 값"
    │       ├── QLabel "f(x) = ?"
    │       └── QLabel "f'(x) = ?"
    └── 우 캔버스 (FigureCanvas, fig 1×1)
        ax: 함수 곡선 + 현재 x 수직선 + 점 + 접선
```

#### 플롯 업데이트 흐름
```
슬라이더/라디오 변경
  → _update()
      → 선택 함수 f, f_d 가져오기
      → x_range = np.linspace(-6, 6, 400)
      → y = f(x_range), dy = f_d(x_range)
      → ax.clear()
      → ax.plot(x_range, y)
      → ax.axvline(x0)
      → ax.scatter([x0], [f(x0)])
      → if show_tangent: 접선 ax.plot
      → label_f.setText(f"f({x0:.2f}) = {f(x0):.4f}")
      → label_d.setText(f"f'({x0:.2f}) = {f_d(x0):.4f}")
      → canvas.draw_idle()
```

### 3.3 `comparison_widget.py` — ComparisonWidget

#### 레이아웃
```
QWidget (ComparisonWidget)
└── QHBoxLayout
    ├── 좌 패널 (width=200)
    │   ├── QGroupBox "함수 선택"
    │   │   └── 4× QCheckBox
    │   ├── QGroupBox "표시 모드"
    │   │   ├── QRadioButton "함수값"
    │   │   └── QRadioButton "미분값"
    │   └── QGroupBox "X 범위"
    │       ├── QSlider (1 ~ 10)
    │       └── QLabel
    └── 우 캔버스 (FigureCanvas, fig 1×1)
```

---

## 4. 데이터 흐름

```
사용자 입력 (라디오/슬라이더/체크박스)
    │
    ▼
[Qt 이벤트 루프]
    │
    ├─ 함수 선택 변경 → ExplorerWidget._update_func()
    ├─ x 슬라이더    → ExplorerWidget._update()
    ├─ α 슬라이더    → ExplorerWidget._update()
    └─ 비교 체크박스 → ComparisonWidget._update()
                             │
                             ▼
                      ax.clear() → ax.plot() × N
                      → canvas.draw_idle()
```

---

## 5. 성능 고려사항

| 항목 | 설계 결정 | 이유 |
|------|-----------|------|
| 함수 해상도 | 400 포인트 | 시각적 품질 vs 속도 균형 |
| `draw_idle()` | `canvas.draw()` 대신 | 불필요한 즉시 flush 방지 |
| `fig.clear()` | axes 재사용 대신 | 메모리 누수 방지 |

---

*문서 끝*
