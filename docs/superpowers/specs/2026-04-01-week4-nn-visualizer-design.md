# Week 4 Neural Network Visualizer — Design Spec
**Date**: 2026-04-01
**Status**: Approved

---

## 1. Product Requirements (PRD)

### 1.1 목적
week4의 4개 Neural Network 실습(함수 근사, 포물선 회귀, 과적합 데모, 진자 예측)을 PySide6 인터랙티브 GUI로 시각화한다. 학습자가 hyperparameter를 조정하고 실시간으로 학습 과정과 결과를 확인할 수 있게 한다.

### 1.2 사용자 목표
- 기본값으로 앱 실행 시 즉시 학습 결과를 확인할 수 있다 (프리셋 자동 학습)
- 파라미터를 바꾸고 재학습하여 결과 차이를 실험할 수 있다
- 여러 Lab 윈도우를 동시에 열어 비교할 수 있다

### 1.3 범위 (In Scope)
- 런처 앱 (4개 Lab 카드 그리드)
- Lab 1: 1D 함수 근사 (Universal Approximation Theorem)
- Lab 2: 포물선 운동 회귀
- Lab 3: 과적합 vs 과소적합 데모
- Lab 4: 진자 주기 예측 + RK4 시뮬레이션
- 각 Lab: 파라미터 조정 + 재학습 + 실시간 loss 곡선

### 1.4 범위 (Out of Scope)
- 모델 저장/불러오기
- 다국어 지원
- 배포 패키징 (installer 등)

---

## 2. Technical Requirements (TRD)

### 2.1 기술 스택
| 항목 | 선택 | 비고 |
|------|------|------|
| GUI | PySide6 | Qt 6 기반 |
| ML | TensorFlow / Keras | week4 기존 코드 재사용 |
| 차트 | Matplotlib (FigureCanvasQTAgg) | PySide6 embed |
| 스레딩 | QThread + Signal/Slot | UI 블로킹 방지 |
| Python | 3.10+ | |

### 2.2 폴더 구조

```
week4/neural_network_visualizer_pyside6/
├── main.py                        # 진입점
├── launcher/
│   ├── launcher_window.py         # QMainWindow, Lab 카드 그리드
│   └── lab_card.py                # 클릭 가능한 Lab 카드 위젯
├── shared/
│   ├── base_lab_window.py         # 3패널 뼈대 + 인터페이스 규약
│   ├── train_worker.py            # QThread 학습 워커 (공통)
│   └── matplotlib_canvas.py      # FigureCanvasQTAgg 래퍼
└── labs/
    ├── lab1_function/
    │   ├── lab_meta.py            # 플러그인 메타데이터
    │   ├── window.py              # BaseLabWindow 상속
    │   └── model.py               # Keras 모델 정의
    ├── lab2_projectile/           # 동일 구조
    ├── lab3_overfitting/          # 동일 구조
    └── lab4_pendulum/             # 동일 구조
```

### 2.3 플러그인 자동 발견 규약

런처 시작 시 `labs/lab*/lab_meta.py`를 glob으로 스캔하여 동적으로 카드 생성.

```python
# labs/lab1_function/lab_meta.py
LAB_META = {
    "id": "lab1_function",
    "title": "Lab 1 · 함수 근사",
    "icon": "📐",
    "description": "Universal Approximation Theorem",
    "window_class": "labs.lab1_function.window.Lab1Window",
}
```

새 Lab 추가 시 `labs/labN_xxx/` 폴더에 `lab_meta.py` 추가만 하면 런처에 자동 등록된다.

### 2.4 BaseLabWindow — 3패널 구조

```
┌─ 헤더 (타이틀 | MIT 6.S191)                      [고양이 SVG] ─┐
├──────────────┬──────────────────────────┬────────────────────┤
│ 좌: 컨트롤   │ 중: 메인 차트            │ 우: 학습 현황      │
│ (200px 고정) │ (FigureCanvasQTAgg)      │ (160px 고정)       │
│              │ flex 확장                │                    │
│ - 공통 파라미 │                          │ - Train/Val Loss   │
│   미터       │                          │ - MAE              │
│   (Layers,   │                          │ - Loss 미니차트    │
│    Epochs,   │                          │ - Lab 고유 수치    │
│    LR, Act.) │                          │                    │
│ - Lab 고유   │                          │                    │
│   파라미터   │                          │                    │
│ - Train/Stop │                          │                    │
│   /Reset 버튼│                          │                    │
│ - Epoch 진행 │                          │                    │
│   바         │                          │                    │
└──────────────┴──────────────────────────┴────────────────────┘
│ 푸터 (기술 정보)                                              │
└───────────────────────────────────────────────────────────────┘
```

서브클래스 구현 인터페이스:
```python
class BaseLabWindow(QMainWindow):
    def _build_custom_controls(self) -> QWidget: ...   # 좌 패널 하단 추가 영역
    def _build_main_chart(self) -> QWidget: ...        # 중앙 차트
    def _build_custom_info(self) -> QWidget: ...       # 우 패널 하단 추가 영역
    def _get_model_and_data(self) -> tuple: ...        # Keras 모델 + 데이터 반환
    def _on_train_complete(self, history): ...         # 학습 완료 후 처리
    def _on_epoch_done(self, epoch, logs): ...         # 에폭마다 차트 갱신
```

### 2.5 QThread 학습 워커

```python
class TrainWorker(QThread):
    epoch_done = Signal(int, dict)   # (epoch, logs)
    train_done = Signal(object)      # history
    train_error = Signal(str)        # error message

    def __init__(self, model, x_train, y_train, epochs, val_split):
        self.stop_flag = False

    def run(self):
        # on_epoch_end 콜백에서 epoch_done emit
        # stop_flag 확인하여 조기 종료

    def stop(self):
        self.stop_flag = True
```

- Train 버튼 → 기존 worker 중단 → 새 TrainWorker 생성 및 start
- Stop 버튼 → `worker.stop()` 호출 → 다음 epoch에서 종료
- 완료/에러 시 signal로 UI 스레드에 전달

### 2.6 학습 방식 (하이브리드)

- 앱 실행 시: 기본 파라미터(`DEFAULT_PARAMS`)로 자동 학습 시작
- 사용자가 파라미터 변경 후 Train 버튼: 기존 학습 중단 → 새 파라미터로 재학습
- Reset 버튼: 파라미터 기본값 복원 + 차트 초기화

### 2.7 Lab별 세부 사양

#### Lab 1 · 함수 근사
| 항목 | 내용 |
|------|------|
| 고유 파라미터 | 함수 선택 (sin(x), cos(x)+0.5sin(2x), x·sin(x)), 네트워크 크기 선택 |
| 메인 차트 | True 함수 vs Predicted 곡선 (x축: -2π ~ 2π) |
| 고유 수치 | MSE, R² |
| 기본 파라미터 | Layers=[128,128,64], Activation=tanh, Epochs=1000, LR=0.001 |

#### Lab 2 · 포물선 회귀
| 항목 | 내용 |
|------|------|
| 고유 파라미터 | 초기속력 v₀ (슬라이더), 발사각도 θ (슬라이더) |
| 메인 차트 | True 궤적 vs Predicted 궤적 (x-y 좌표) |
| 고유 수치 | 최대 높이 오차, 사거리 오차 |
| 기본 파라미터 | Layers=[128,64,32], Activation=relu, Epochs=500, LR=0.001 |

#### Lab 3 · 과적합 데모
| 항목 | 내용 |
|------|------|
| 고유 파라미터 | 모델 선택 (Underfit/Good/Overfit), Dropout 비율 |
| 메인 차트 | 3개 모델 예측 곡선 동시 비교 |
| 고유 수치 | Train/Val Loss 갭, 과적합 판단 |
| 특이사항 | 3개 모델을 순차 학습 후 한 차트에 표시 |

#### Lab 4 · 진자 예측
| 항목 | 내용 |
|------|------|
| 고유 파라미터 | 진자 길이 L (슬라이더), 초기 각도 θ₀ (슬라이더) |
| 메인 차트 | 주기 예측 곡선 + RK4 시뮬레이션 (θ vs t) |
| 고유 수치 | MAPE, 이론값 vs 예측값 비교 |
| 기본 파라미터 | Layers=[64,32,16], Activation=relu, Epochs=500, LR=0.001 |

### 2.8 디자인 시스템 (Dark Theme — Tokyo Night 기반)

```python
COLORS = {
    "bg":           "#1a1b26",   # 메인 배경
    "panel":        "#16213e",   # 사이드 패널
    "card":         "#1e2030",   # 카드·입력 배경
    "border":       "#2a2d3e",   # 구분선
    "border_light": "#3b4261",   # 입력 테두리
    "accent":       "#7aa2f7",   # 주 액센트 (파랑)
    "success":      "#9ece6a",   # 진행바·성공 (초록)
    "danger":       "#f7768e",   # Stop·경고 (빨강)
    "highlight":    "#e0af68",   # 강조 (노랑)
    "text":         "#c0caf5",   # 기본 텍스트
    "text_dim":     "#a9b1d6",   # 보조 텍스트
    "text_muted":   "#565f89",   # 비활성 텍스트
}
```

#### 고양이 마스코트
헤더 우측 상단에 36×36px SVG 고양이 (Tokyo Night 컬러 적용, 앞발 모은 앉은 자세, 수염·귀 분홍·꼬리 포함). 방해가 되지 않도록 `opacity: 0.85`.

### 2.9 matplotlib dark 설정
```python
plt.style.use('dark_background')
# figure facecolor: #1e2030
# axes facecolor:   #1a1b26
# grid color:       #2a2d3e
```

---

## 3. 결정 요약

| 결정 항목 | 선택 | 이유 |
|-----------|------|------|
| 앱 구조 | 런처 + 독립 서브윈도우 | 동시 비교 가능, 확장성 |
| Lab 발견 | 플러그인 자동 발견 | `lab_meta.py` 추가만으로 등록 |
| 학습 방식 | 하이브리드 (프리셋 + 재학습) | 즉시 결과 + 실험 가능 |
| 차트 | Matplotlib embed | 기존 week4 코드 재사용 |
| 레이아웃 | 3패널 (좌·중·우) | week3 CNN 패턴 일관성 |
| 스레딩 | QThread + Signals | PySide6 표준, 취소 가능 |
| 테마 | Dark (Tokyo Night) | 사용자 선호 |
| 마스코트 | 헤더 우측 고양이 SVG | 귀엽고 방해 안 됨 |
