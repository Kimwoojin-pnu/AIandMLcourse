# TRD — Technical Requirements Document
# CNN 합성곱 필터 시각화 프로그램

| 항목 | 내용 |
|------|------|
| 문서 버전 | v2.0 |
| 작성자 | 김우진 |
| 작성일 | 2026-03-26 |
| 참조 PRD | PRD.md v2.0 |
| 변경 이력 | v1.0 → v2.0: 해상도 8×8 → 128×128, Entry 그리드 → PIL Canvas, Auto 배치 처리 도입 |

---

## 1. 기술 스택 및 환경

| 구분 | 선택 | 선택 이유 |
|------|------|----------|
| 언어 | Python 3.8+ | 데이터 처리·GUI 통합 용이, 별도 빌드 불필요 |
| GUI 프레임워크 | tkinter (표준 라이브러리) | 추가 설치 없이 Python에 내장, VS Code 터미널에서 즉시 실행 |
| 이미지 처리·렌더링 | Pillow (PIL) | PNG/JPG 로드, 그레이스케일 변환, 리사이즈, Canvas용 PhotoImage 생성 |
| 수치 연산 | Python 내장 (list) | NumPy 미사용, 의존성 최소화 |
| 실행 방법 | `python main.py` | 단일 진입점, 추가 설정 없음 |

```bash
# 의존성 설치 (최초 1회)
pip install pillow
```

---

## 2. 파일 구조

```
cnn_filter_visualizer/
├── main.py                   # 진입점 – App 클래스 생성 및 mainloop 실행
├── app.py                    # App 클래스 – 전체 창 레이아웃 + 상태 관리
├── panels/
│   ├── __init__.py
│   ├── input_panel.py        # 왼쪽 패널: 256×256 Canvas 이미지 표시 + 파일 업로드
│   ├── control_panel.py      # 중앙 패널: 필터 선택 + 계산식 + 버튼
│   └── output_panel.py       # 오른쪽 패널: 252×252 Canvas Feature Map
├── logic/
│   ├── __init__.py
│   ├── convolution.py        # 합성곱 연산 순수 함수 (N×N 범용)
│   └── filters.py            # 필터 커널 상수 정의
├── utils/
│   ├── __init__.py
│   └── image_loader.py       # PIL 이미지 로드 → 128×128 정수 배열 변환
├── PRD.md
└── TRD.md
```

---

## 3. 모듈별 설계

### 3-1. `logic/filters.py` — 필터 상수 (변경 없음)

```python
FILTERS = {
    "Sharpen":      {"kernel": [[0,-1,0],[-1,5,-1],[0,-1,0]],  "mode": "clamp", ...},
    "Edge Detect":  {"kernel": [[0,1,0],[1,-4,1],[0,1,0]],     "mode": "abs",   ...},
    "Sobel X":      {"kernel": [[-1,0,1],[-2,0,2],[-1,0,1]],   "mode": "abs",   ...},
}
FILTER_NAMES = list(FILTERS.keys())
```

### 3-2. `logic/convolution.py` — 핵심 연산 (범용화)

```python
def compute_one(pixels, kernel, row, col, mode) -> dict:
    """
    pixels : N×N int list-of-list (N은 가변)
    kernel : 3×3 int list-of-list
    row, col : 출력 위치 (0 ~ N-3)
    반환: { patch, kflat, products, raw_sum, output_val }
    """

def compute_all(pixels, kernel, mode) -> list[list[int]]:
    """out_n = len(pixels) - 2 로 동적 계산 (range(6) 하드코딩 제거)"""
```

### 3-3. `utils/image_loader.py` — 이미지 로드

```python
IMG_N = 128   # 해상도 상수

def load_image_as_grid(filepath: str) -> list[list[int]]:
    """PNG/JPG → Grayscale → 128×128 → int list"""
    img = Image.open(filepath).convert('L')
    img = img.resize((IMG_N, IMG_N), Image.LANCZOS)
    return [[img.getpixel((c, r)) for c in range(IMG_N)] for r in range(IMG_N)]

# 기본 패턴: 좌절반=200, 우절반=30 수직 경계
DEFAULT_PIXELS = [
    [200 if c < IMG_N // 2 else 30 for c in range(IMG_N)]
    for _ in range(IMG_N)
]
```

### 3-4. `panels/input_panel.py` — 입력 패널 (Canvas 기반)

```python
IMG_DISPLAY = 256   # 캔버스 크기 (px)
IMG_PIXEL   = 2     # IMG_DISPLAY // IMG_N

class InputPanel(tk.Frame):
    _pixels : list[list[int]]   # 128×128 내부 픽셀 버퍼
    _photo  : ImageTk.PhotoImage  # GC 방지용 참조 유지
    _hl_item: int | None          # 하이라이트 Canvas 아이템 ID

    def get_pixels(self) -> list[list[int]]:
        """내부 버퍼 복사본 반환"""

    def set_pixels(self, pixels):
        """128×128 배열 저장 → _redraw_image() 호출"""

    def highlight(self, row, col):
        """(row, col) 기준 3×3 창을 빨간 테두리 사각형으로 표시"""

    def _redraw_image(self):
        """PIL frombytes → resize(NEAREST) → PhotoImage → create_image"""
```

### 3-5. `panels/control_panel.py` — 제어 패널

```python
class ControlPanel(tk.Frame):
    def __init__(self, parent, app, total_steps: int): ...
    filter_var    : tk.StringVar
    speed_var     : tk.IntVar       # 1~10
    _total_steps  : int             # 15,876 (동적 전달)

    def update_progress(self, step_idx):
        """f"{step_idx:,} / {self._total_steps:,}" 형식으로 표시"""
```

### 3-6. `panels/output_panel.py` — 출력 패널 (Canvas + PIL 버퍼)

```python
OUT_N       = IMG_N - 2   # 126
OUT_DISPLAY = OUT_N * 2   # 252
OUT_PIXEL   = 2

class OutputPanel(tk.Frame):
    _out_img   : Image.Image          # PIL 픽셀 버퍼 (126×126 "L" 모드)
    _out_photo : ImageTk.PhotoImage   # GC 방지용 참조
    _img_id    : int | None           # Canvas create_image 아이템 ID

    def set_value(self, row, col, value):
        """putpixel + 즉시 _update_canvas() — 수동 Step용"""

    def put_value(self, row, col, value):
        """putpixel만 (캔버스 갱신 없음) — Auto 배치용"""

    def refresh(self):
        """_update_canvas() — Auto 배치 후 1회 호출"""

    def _update_canvas(self):
        """PIL resize(NEAREST, 252×252) → PhotoImage → itemconfig"""
```

### 3-7. `app.py` — 상태 관리

```python
IMG_N       = 128    # (image_loader에서 import)
OUT_N       = 126    # IMG_N - 2
TOTAL_STEPS = 15876  # OUT_N ** 2

class App(tk.Tk):
    _step_idx   : int             # 0 ~ 15876
    _auto_id    : int | None      # after() 반환값

    def step(self):
        """수동 1스텝: compute_one → 즉시 UI 갱신"""

    def toggle_auto(self):
        """Auto 시작/일시정지 토글"""

    def _auto_batch(self):
        """
        speed² 스텝을 한 배치로 처리 후 캔버스 1회 갱신.
        steps_per_frame = speed²  (1 ~ 100)
        delay           = max(16, 500 // speed) ms
        → speed=10 시 약 2,000 스텝/초, 전체 ~8초 완료
        """

    def reset(self):
        """after_cancel, step_idx=0, Feature Map 초기화"""
```

---

## 4. 데이터 흐름

| 순서 | 이벤트 | 처리 내용 |
|------|--------|----------|
| 1 | 앱 시작 | DEFAULT_PIXELS(128×128) 로드, Canvas 렌더링, Feature Map 초기화 |
| 2 | 파일 업로드 | `load_image_as_grid()` → `set_pixels()` → `_redraw_image()` → `reset()` |
| 3 | 필터 선택 변경 | 커널 라벨 갱신 → `reset()` |
| 4 | Step 클릭 | `compute_one()` → 입력 하이라이트(오버레이) → `set_value()`(즉시 갱신) → 계산식 표시 |
| 5 | Auto 클릭 | `_auto_batch()`: 배치 계산 → `put_value()` × N → `refresh()` 1회 → `after()` |
| 6 | Reset 클릭 | `after_cancel()`, `step_idx=0`, 패널 초기화 |

---

## 5. UI 설계 상세

### 5-1. 색상

| 요소 | 색상 |
|------|------|
| 입력 Canvas 기본 | 128×128 그레이스케일 이미지 |
| 슬라이딩 창 하이라이트 | `#FF4444` (빨간 테두리, 2px) |
| 커널 양수값 | `#E6F1FB` |
| 커널 음수값 | `#FAECE7` |
| 커널 0값 | `#F0F0F0` |
| Feature Map 완료 셀 | PIL putpixel → `rgb(v,v,v)` 그레이 |
| Feature Map 미완료 | `200` (EMPTY_GRAY, 연회색) |
| Feature Map 현재 위치 | `#3399FF` 테두리 (2px) |

### 5-2. Auto 속도 테이블

| speed | steps_per_frame | delay (ms) | 스텝/초 | 전체 완료 예상 |
|-------|----------------|-----------|--------|-------------|
| 1 | 1 | 500 | 2 | ~130분 |
| 3 | 9 | 166 | 54 | ~5분 |
| 5 | 25 | 100 | 250 | ~63초 |
| 7 | 49 | 71 | 690 | ~23초 |
| 10 | 100 | 50 | 2,000 | ~8초 |

### 5-3. 계산식 표시 포맷

```
[입력 패치 3×3]  ×  [커널 3×3]  =  [원소별 곱 3×3]
모두 더하면: {raw_sum}  →  {mode 처리}  →  출력값: {output_val}
```

---

## 6. 에러 처리

| 상황 | 처리 방법 |
|------|----------|
| 지원하지 않는 이미지 형식 | `messagebox.showerror()` 알림 |
| 이미지 로드 실패 | `messagebox.showerror()` 알림, 기존 픽셀 유지 |
| Step 완료 후 추가 클릭 | `step_idx >= TOTAL_STEPS` 시 early return |
| PIL 미설치 | ImportError → showerror 후 종료 안내 |

---

## 7. 테스트 케이스

| TC | 항목 | 입력 | 기대 결과 |
|----|------|------|----------|
| TC-01 | 균일 패치 Edge Detect | 전체 200, Edge Detect | 대부분 output_val = 0 |
| TC-02 | 수직 에지 Sobel X | 기본 패턴(좌200/우30), Sobel X | 경계 열 Feature Map 밝게, 균일 영역 = 0 |
| TC-03 | Step 완료 | 모든 Step 완료 | step_idx = 15,876, Feature Map 채워짐 |
| TC-04 | Auto 일시정지 | Auto 시작 → 일시정지 | 재개 시 step_idx 연속 진행 |
| TC-05 | 파일 업로드 | PNG 선택 | 캔버스에 128×128 그레이스케일 이미지 표시 |
| TC-06 | Reset 후 재시작 | Step 10회 → Reset → Step | step_idx = 0부터 재시작, Feature Map 회색 초기화 |
| TC-07 | Auto speed=10 성능 | Auto, speed=10 | 전체 15,876 스텝 10초 이내 완료 |

---

## 8. 개발 단계 (완료 순서)

1. `filters.py` — 기존 유지
2. `convolution.py` — compute_all 동적 크기 처리
3. `image_loader.py` — IMG_N=128, load_image_as_grid, DEFAULT_PIXELS 교체
4. `input_panel.py` — Entry 그리드 제거, PIL Canvas 기반 재작성
5. `output_panel.py` — Label 그리드 제거, PIL Canvas 기반 재작성
6. `control_panel.py` — total_steps 파라미터 + 진행 포맷 업데이트
7. `app.py` — OUT_N/TOTAL_STEPS 상수, `_auto_batch()` 배치 처리 도입
