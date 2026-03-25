# TRD — 범용 근사 학습 도구 (Universal Approximation Visualizer)

> **버전:** 1.0.0
> **기술 스택:** Python 3.10+ / PySide6 / NumPy / Matplotlib

---

## 1. 기술 스택

| 계층 | 라이브러리 | 버전 | 역할 |
|------|-----------|------|------|
| GUI 프레임워크 | PySide6 (Qt6) | ≥ 6.5 | 위젯, QTimer |
| 수치 계산 | NumPy | ≥ 1.24 | 행렬 연산 |
| 시각화 | Matplotlib | ≥ 3.7 | 근사 플롯, MSE 표시 |

---

## 2. 프로젝트 파일 구조

```
universal_approximation_visualizer/
├── main.py
├── main_window.py
├── theory_widget.py
├── approximation_widget.py  # 함수 근사 탭 (QTimer 학습 애니메이션)
├── comparison_widget.py     # 뉴런 수 비교 탭 (3개 모델 병렬)
├── approximator_model.py    # UniversalApproximator 순수 로직
├── styles.py
├── utils.py
└── requirements.txt
```

---

## 3. 모듈별 상세 명세

### 3.1 `approximator_model.py`

```
TARGET_FUNCTIONS: dict[str, callable]
  "Sine Wave"       → sin(2πx)
  "Step Function"   → where(x < 0.5, 0, 1)
  "Complex"         → sin(2πx) + 0.5*sin(4πx) + 0.3*cos(6πx)

UniversalApproximator
├── __init__(n_hidden, lr, activation='tanh')
│     W1: (1, n_hidden) Xavier uniform
│     b1: (n_hidden,) zeros
│     W2: (n_hidden, 1) Xavier uniform
│     b2: (1,) zeros
│     loss_history: list[float]
│     step: int
│
├── reset(n_hidden, lr)
│
├── forward(x) → y_pred
│
├── train_step(x_train, y_train) → loss
│     forward → MSE → backward → update
│     loss_history.append; step += 1
│
└── get_mse(x_test, y_test) → float
```

### 3.2 `approximation_widget.py` — ApproximationWidget

#### QTimer 학습 루프
```
[학습 시작]
  → timer.start(interval)

[timeout 매 tick]
  → STEPS_PER_TICK = 50 (빠른 학습)
  → for _ in range(STEPS_PER_TICK): model.train_step()
  → _draw()
      → ax[0]: 실제 함수(파랑) + NN 예측(빨강 점선) + 학습 데이터(초록 점)
      → ax[1]: Loss 곡선
      → mse_label 갱신
  → step >= max_epochs → timer.stop()
```

#### 레이아웃
```
QWidget
└── QHBoxLayout
    ├── 좌 패널 (width=280)
    │   ├── QGroupBox "목표 함수"
    │   │   └── 3× QRadioButton
    │   ├── QGroupBox "네트워크"
    │   │   ├── QSlider "뉴런 수" (2~100) + QLabel
    │   │   └── QDoubleSpinBox "학습률"
    │   ├── QGroupBox "학습"
    │   │   ├── QSpinBox "에포크"
    │   │   └── QSlider "속도"
    │   ├── 버튼 (학습 시작 / 초기화)
    │   └── QLabel "MSE: 0.0000" (크게)
    └── 우 캔버스 (FigureCanvas)
        fig (2×1):
          ax[0]: 함수 비교 플롯
          ax[1]: Loss 곡선 (log scale)
```

### 3.3 `comparison_widget.py` — ComparisonWidget

```
QWidget
└── QVBoxLayout
    ├── 상단 컨트롤 (함수 선택 라디오 + "모두 학습" 버튼)
    └── FigureCanvas
        fig (1×3):
          ax[0]: 3 뉴런  (MSE 표시)
          ax[1]: 10 뉴런 (MSE 표시)
          ax[2]: 50 뉴런 (MSE 표시)
```

"모두 학습" 클릭 시:
1. 3개 UniversalApproximator 생성
2. 각각 5000 에포크 학습 (UI blocking 없이 루프)
3. 결과 플롯

---

## 4. 데이터 흐름

```
[목표 함수 변경] → model.reset() → _draw()
[뉴런 수 변경]   → model.reset() → _draw()
[학습 시작]      → QTimer.start()
  timeout → model.train_step() × STEPS_PER_TICK → _draw()
```

---

## 5. 성능 고려사항

| 항목 | 설계 결정 |
|------|-----------|
| 학습 포인트 | 100개 (x_train) |
| 플롯 해상도 | 200 포인트 (x_test) |
| STEPS_PER_TICK | 50 (애니메이션 부드럽게) |
| comparison 학습 | 5000 에포크 × 3 모델 (blocking loop, 빠름) |

---

*문서 끝*
