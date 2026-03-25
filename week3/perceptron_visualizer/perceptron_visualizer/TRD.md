# TRD — 퍼셉트론 학습 도구 (Perceptron Visualizer)

> **버전:** 1.0.0  
> **기술 스택:** Python 3.10+ / PySide6 / NumPy / Matplotlib  

---

## 1. 기술 스택

| 계층 | 라이브러리/프레임워크 | 버전 | 역할 |
|------|----------------------|------|------|
| GUI 프레임워크 | PySide6 (Qt6) | ≥ 6.5 | 위젯, 레이아웃, 이벤트 루프 |
| 수치 계산 | NumPy | ≥ 1.24 | 행렬 연산, 결정 경계 메쉬 |
| 시각화 | Matplotlib | ≥ 3.7 | 그래프 렌더링 (Qt 백엔드 embed) |
| Matplotlib 백엔드 | `backend_qtagg` | (Matplotlib 내장) | Qt 캔버스에 Figure 임베드 |
| 언어 | Python | ≥ 3.10 | 타입 힌트 (`list[dict]` 등) |

---

## 2. 프로젝트 파일 구조

```
perceptron_visualizer/
│
├── main.py                  # 진입점 (QApplication, MainWindow 시작)
│
├── main_window.py           # QMainWindow: 헤더 + QTabWidget + 푸터
│
├── theory_widget.py         # QWidget: 이론 설명 (QTextBrowser + HTML)
│
├── simulation_widget.py     # QWidget: 학습 시뮬레이션 (QTimer + FigureCanvas)
│
├── manual_widget.py         # QWidget: 가중치·편향 직접 조작 (슬라이더 + 플롯)
│
├── perceptron_model.py      # 퍼셉트론 클래스 (비-GUI 순수 로직)
│
├── styles.py                # Qt 스타일시트 상수 모음
│
├── utils.py                 # 한글 폰트 설정, 게이트 데이터 상수
│
└── requirements.txt         # pip 의존성 목록
```

---

## 3. 모듈별 상세 명세

### 3.1 `perceptron_model.py` — Perceptron 클래스

```
Perceptron
├── __init__(learning_rate: float = 0.1)
│     weights: np.ndarray[2]   ← randn * 0.5
│     bias:    float           ← randn * 0.5
│     history: list[dict]      ← 에포크별 기록
│
├── reset()
│     가중치·편향 재초기화 + history 클리어
│
├── net_input(inputs) → float
│     z = w · x + b
│
├── predict_single(inputs) → int
│     step(net_input(inputs))
│
├── predict_batch(X) → ndarray
│     [predict_single(x) for x in X]
│
└── train_one_epoch(X, y) → float (accuracy)
      for each (x_i, y_i):
        error = y_i - predict_single(x_i)
        weights += lr * error * x_i
        bias    += lr * error
      record history
      return accuracy
```

**히스토리 레코드 스키마 (dict):**

```python
{
    "epoch":    int,    # 1-based
    "w1":       float,
    "w2":       float,
    "bias":     float,
    "accuracy": float,  # 0.0 ~ 1.0
}
```

---

### 3.2 `simulation_widget.py` — SimulationWidget

#### 상태 변수

| 변수 | 타입 | 설명 |
|------|------|------|
| `_gate` | `str` | 현재 선택된 게이트 (`"AND"` / `"OR"` / `"XOR"`) |
| `_epoch` | `int` | 현재까지 진행한 에포크 수 |
| `_max_epochs` | `int` | 목표 에포크 수 (epoch_spin 값) |
| `_perceptron` | `Perceptron` | 현재 학습 중인 모델 인스턴스 |
| `_timer` | `QTimer` | 에포크별 애니메이션 타이머 |

#### QTimer 흐름

```
[▶ 클릭]
    → timer.setInterval(speed_map[slider])
    → timer.start()

[timeout 신호 (매 tick)]
    → _step()
        → perceptron.train_one_epoch(X, y)
        → epoch += 1
        → log_table 행 추가
        → _draw() 호출  (Figure clear → contourf → canvas.draw_idle)
        → 수렴/완료 조건 체크 → timer.stop()

[⏸ 클릭]
    → timer.stop()
    → 버튼 텍스트 "▶ 재개"
```

#### 시각화 (Matplotlib 2-subplot)

| Subplot | 내용 | 사용 API |
|---------|------|----------|
| 왼쪽 (1,2,1) | 결정 경계 + 데이터 포인트 | `contourf`, `contour`, `scatter` |
| 오른쪽 (1,2,2) | 에포크별 정확도 변화 | `plot`, `fill_between`, `axhline` |

**결정 경계 계산 최적화:**
```python
# NumPy 브로드캐스팅으로 meshgrid 전체를 한 번에 계산
nets = w1 * xx + w2 * yy + b
Z = (nets >= 0).astype(int)
# → predict_single 루프 없이 250×250 = 62,500 포인트 즉시 계산
```

---

### 3.3 `manual_widget.py` — ManualWidget

#### `_ParamSlider` 내부 클래스

- `QSlider` 범위: `[-300, 300]` (실제값 ×100)
- 슬라이더 값 → 실수: `value / 100.0`
- `set_value(v)` : `blockSignals(True)` → setValue → `blockSignals(False)`
  → 재귀 업데이트 방지

#### 시각화 (Matplotlib 2-subplot)

| Subplot | 내용 | 비고 |
|---------|------|------|
| 왼쪽 (1,2,1) | 결정 경계 (이진 contourf) | 슬라이더 즉시 반영 |
| 오른쪽 (1,2,2) | 순입력 z 연속 히트맵 | `RdBu_r` colormap, colorbar |

---

### 3.4 `theory_widget.py` — TheoryWidget

- `QTextBrowser` + `setHtml()` 로 구조화된 HTML 렌더링
- 인라인 CSS로 `formula-box`, `note`, `warning`, `success` 스타일 클래스 정의
- 스크롤바 커스터마이징 (슬림 8px)

---

### 3.5 `main_window.py` — MainWindow

```
QMainWindow
└── centralWidget (QWidget)
    └── QVBoxLayout
        ├── header (QWidget, height=58, bg=#1a2634)
        │     QHBoxLayout: logo | stretch | subtitle
        │
        ├── QTabWidget (documentMode=True)
        │     Tab 0: TheoryWidget
        │     Tab 1: SimulationWidget
        │     Tab 2: ManualWidget
        │
        └── footer (QWidget, height=28, bg=#f0f4f8)
              학습 순서 안내 텍스트
```

---

## 4. 데이터 흐름

```
사용자 입력 (슬라이더/버튼/라디오)
        │
        ▼
[Qt 이벤트 루프]
        │
        ├─ gate changed  → SimulationWidget._reset()
        ├─ lr changed    → perceptron.lr = new_lr
        ├─ train clicked → QTimer.start() / stop()
        ├─ QTimer.timeout → _step() → Perceptron.train_one_epoch()
        └─ slider moved  → ManualWidget._update_all()
                                │
                                ▼
                         _update_formula()    → QLabel setText
                         _update_pred_table() → QTableWidget setItem
                         _update_plot()       → Figure.clear()
                                              → ax.contourf / plot
                                              → canvas.draw_idle()
```

---

## 5. 성능 고려사항

| 항목 | 설계 결정 | 이유 |
|------|-----------|------|
| contourf 해상도 | 250×250 포인트 | 시각적 품질 vs 속도 균형 |
| 타이머 최소 간격 | 3ms (최고속) | Qt 이벤트 루프 블로킹 방지 |
| `draw_idle()` 사용 | `canvas.draw()` 대신 | 불필요한 즉시 flush 방지 |
| `blockSignals` | `_ParamSlider.set_value()` | 프리셋 적용 시 N번 재귀 방지 |
| Figure clear 방식 | `fig.clear()` + `add_subplot` | axes 재사용 시 메모리 누수 회피 |

---

## 6. 에러 처리

| 상황 | 처리 방식 |
|------|-----------|
| `contour(levels=[0.5])` — 등위선 없음 | `try/except` 로 무시 (Z 전부 0 또는 1) |
| w₁=w₂=0 일 때 결정 경계 수식 | 분기 처리 → "없음 (w₁=w₂=0)" 표시 |
| w₂=0 결정 경계 텍스트 | "수직선 (x₁ = …)" 표시 |
| matplotlib 한글 폰트 없음 | 후보 목록 순차 시도 → 없으면 기본 폰트 |

---

## 7. 설치 및 실행 가이드

```bash
# 1. 저장소/디렉터리 이동
cd perceptron_visualizer

# 2. (권장) 가상 환경 생성
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 실행
python main.py
```

### 한글 폰트 설치 (Linux)

```bash
sudo apt-get install fonts-nanum   # Ubuntu/Debian
fc-cache -fv                        # 폰트 캐시 갱신
```

---

## 8. 확장 계획 (Future Work)

| 기능 | 설명 |
|------|------|
| MLP 탭 추가 | XOR 해결을 위한 2층 퍼셉트론 시뮬레이션 |
| 커스텀 데이터 입력 | 캔버스 클릭으로 학습 포인트 추가 |
| 학습 기록 저장 | JSON 내보내기 / 불러오기 |
| 다양한 활성화 함수 | Sigmoid, ReLU 전환 비교 |
| 학습률 스케줄러 시각화 | epoch에 따른 η 감소 애니메이션 |

---

*문서 끝*
