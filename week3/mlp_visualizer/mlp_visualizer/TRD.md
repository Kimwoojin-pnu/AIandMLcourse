# TRD — MLP 학습 도구 (MLP Visualizer)

> **버전:** 1.0.0
> **기술 스택:** Python 3.10+ / PySide6 / NumPy / Matplotlib

---

## 1. 기술 스택

| 계층 | 라이브러리 | 버전 | 역할 |
|------|-----------|------|------|
| GUI 프레임워크 | PySide6 (Qt6) | ≥ 6.5 | 위젯, 레이아웃, QTimer |
| 수치 계산 | NumPy | ≥ 1.24 | 행렬 연산, 역전파 |
| 시각화 | Matplotlib | ≥ 3.7 | 결정 경계, Loss 곡선, 히트맵 |

---

## 2. 프로젝트 파일 구조

```
mlp_visualizer/
├── main.py
├── main_window.py
├── theory_widget.py
├── simulation_widget.py     # XOR 학습 시뮬레이션 (QTimer + 결정경계)
├── gradient_widget.py       # 경사 시각화 (dW1, dW2 히트맵)
├── mlp_model.py             # MLP 순수 로직 (forward, backward, train_step)
├── styles.py
├── utils.py
└── requirements.txt
```

---

## 3. 모듈별 상세 명세

### 3.1 `mlp_model.py` — MLPModel

```
MLPModel
├── __init__(hidden_size=4, lr=0.5)
│     W1: (2, hidden_size) Xavier init
│     b1: (1, hidden_size) zeros
│     W2: (hidden_size, 1) Xavier init
│     b2: (1, 1) zeros
│     loss_history: list[float]
│     epoch: int
│     dW1, dW2: 마지막 경사 (히트맵용)
│
├── reset(hidden_size, lr)
│     가중치 재초기화 + 히스토리 클리어
│
├── forward(X) → a2: ndarray
│     z1 = X @ W1 + b1;  a1 = sigmoid(z1)
│     z2 = a1 @ W2 + b2;  a2 = sigmoid(z2)
│
├── train_step(X, y) → loss: float
│     forward → MSE loss → backward → update
│     self.dW1, self.dW2 저장
│     loss_history.append; epoch += 1
│     return loss
│
└── predict(X) → ndarray  (> 0.5 → 1)

X_XOR = [[0,0],[0,1],[1,0],[1,1]]
y_XOR = [[0],[1],[1],[0]]
```

### 3.2 `simulation_widget.py` — SimulationWidget

#### QTimer 흐름 (perceptron_visualizer와 동일 패턴)
```
[▶ 클릭]
  → timer.setInterval(speed_map[slider])
  → timer.start()

[timeout]
  → _step()
      → model.train_step(X_XOR, y_XOR)
      → log_table 행 추가
      → _draw() 호출
          → 결정경계 subplot (contourf 200×200)
          → Loss 곡선 subplot (log scale)
      → 정확도 100% → timer.stop() + 완료 메시지
```

#### 레이아웃
```
QWidget
└── QHBoxLayout
    ├── 좌 패널 (width=280)
    │   ├── QGroupBox "모델 설정"
    │   │   ├── QSpinBox "은닉 뉴런" (2~16)
    │   │   └── QDoubleSpinBox "학습률" (0.01~2.0, 0.01)
    │   ├── QGroupBox "학습 설정"
    │   │   ├── QSpinBox "총 에포크" (100~50000)
    │   │   └── QSlider "속도"
    │   ├── 버튼 행 (시작 / 일시정지 / 초기화)
    │   └── QTableWidget 로그 (에포크, Loss, 정확도)
    └── 우 캔버스 (FigureCanvas)
        fig (1×2):
          ax[0]: XOR 결정 경계 contourf
          ax[1]: Loss 곡선 (log scale)
```

### 3.3 `gradient_widget.py` — GradientWidget

```
QWidget
└── FigureCanvas
    fig (2×2):
      ax[0,0]: dW1 imshow (input×hidden)
      ax[0,1]: dW2 imshow (hidden×1)
      ax[1,0]: 레이어별 경사 크기 bar chart
      ax[1,1]: 은닉층 활성화 heatmap (4샘플 × n_hidden)
```

SimulationWidget이 `train_step` 후 `gradient_widget.refresh(model)` 호출.

---

## 4. 데이터 흐름

```
[▶ 시작] → QTimer.start()
    → timeout → MLPModel.train_step()
        → SimulationWidget._draw()  (결정경계 + Loss)
        → GradientWidget.refresh()  (dW1, dW2 히트맵)
```

---

## 5. 성능 고려사항

| 항목 | 설계 결정 |
|------|-----------|
| 결정경계 해상도 | 200×200 |
| 타이머 최소 간격 | 3ms |
| GradientWidget 갱신 | 10 step마다 1회 (빈도 낮춤) |

---

*문서 끝*
