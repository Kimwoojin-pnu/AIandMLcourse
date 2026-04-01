# Week 4 Neural Network Visualizer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** PySide6 다크 테마 런처 앱 + 4개 Lab 서브윈도우 (함수 근사 / 포물선 / 과적합 / 진자), 플러그인 자동 발견, QThread 학습, Matplotlib embed.

**Architecture:** 런처가 `labs/lab*/lab_meta.py`를 glob 스캔 → 카드 동적 생성 → 클릭 시 서브윈도우 열림. `shared/base_lab_window.py`가 3패널 뼈대와 QThread 워커를 제공. 각 Lab은 `_build_custom_controls / _build_main_chart / _get_model_and_data / _on_train_complete` 4개 메서드만 구현.

**Tech Stack:** Python 3.12 (`.venv`), PySide6 6.11.0, TensorFlow 2.21.0, Matplotlib 3.10.7

**Run:** `.venv/Scripts/python.exe week4/neural_network_visualizer_pyside6/main.py`
**Test:** `.venv/Scripts/python.exe -m pytest week4/neural_network_visualizer_pyside6/tests/ -v`

---

## File Map

```
week4/neural_network_visualizer_pyside6/
├── main.py
├── conftest.py                        ← pytest sys.path 설정
├── tests/
│   ├── test_train_worker.py
│   ├── test_models.py
│   └── test_plugin_discovery.py
├── launcher/
│   ├── __init__.py
│   ├── launcher_window.py
│   └── lab_card.py
├── shared/
│   ├── __init__.py
│   ├── colors.py
│   ├── matplotlib_canvas.py
│   ├── train_worker.py
│   └── base_lab_window.py
└── labs/
    ├── __init__.py
    ├── lab1_function/
    │   ├── __init__.py
    │   ├── lab_meta.py
    │   ├── model.py
    │   └── window.py
    ├── lab2_projectile/
    │   ├── __init__.py
    │   ├── lab_meta.py
    │   ├── model.py
    │   └── window.py
    ├── lab3_overfitting/
    │   ├── __init__.py
    │   ├── lab_meta.py
    │   ├── model.py
    │   └── window.py
    └── lab4_pendulum/
        ├── __init__.py
        ├── lab_meta.py
        ├── model.py
        └── window.py
```

---

## Task 1: 프로젝트 뼈대 + colors.py

**Files:**
- Create: `week4/neural_network_visualizer_pyside6/shared/__init__.py`
- Create: `week4/neural_network_visualizer_pyside6/shared/colors.py`
- Create: `week4/neural_network_visualizer_pyside6/launcher/__init__.py`
- Create: `week4/neural_network_visualizer_pyside6/labs/__init__.py`
- Create: `week4/neural_network_visualizer_pyside6/labs/lab1_function/__init__.py` (+ lab2, lab3, lab4)
- Create: `week4/neural_network_visualizer_pyside6/conftest.py`

- [ ] **Step 1: 디렉토리 + 빈 __init__.py 생성**

```bash
cd "week4/neural_network_visualizer_pyside6"
# Windows
mkdir launcher shared labs\lab1_function labs\lab2_projectile labs\lab3_overfitting labs\lab4_pendulum tests
type nul > launcher\__init__.py
type nul > shared\__init__.py
type nul > labs\__init__.py
type nul > labs\lab1_function\__init__.py
type nul > labs\lab2_projectile\__init__.py
type nul > labs\lab3_overfitting\__init__.py
type nul > labs\lab4_pendulum\__init__.py
type nul > tests\__init__.py
```

- [ ] **Step 2: shared/colors.py 작성**

```python
# shared/colors.py
COLORS = {
    "bg":           "#1a1b26",
    "panel":        "#16213e",
    "card":         "#1e2030",
    "border":       "#2a2d3e",
    "border_light": "#3b4261",
    "accent":       "#7aa2f7",
    "success":      "#9ece6a",
    "danger":       "#f7768e",
    "highlight":    "#e0af68",
    "text":         "#c0caf5",
    "text_dim":     "#a9b1d6",
    "text_muted":   "#565f89",
}

CAT_SVG = b"""<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36">
  <ellipse cx="18" cy="26" rx="9" ry="7" fill="#a9b1d6"/>
  <circle cx="18" cy="16" r="8" fill="#a9b1d6"/>
  <polygon points="10,11 8,4 15,9" fill="#a9b1d6"/>
  <polygon points="11,10 9,5 14,9" fill="#f7768e" opacity="0.7"/>
  <polygon points="26,11 28,4 21,9" fill="#a9b1d6"/>
  <polygon points="25,10 27,5 22,9" fill="#f7768e" opacity="0.7"/>
  <ellipse cx="15" cy="16" rx="1.8" ry="2.2" fill="#1a1b26"/>
  <circle cx="15.5" cy="15.3" r="0.6" fill="#fff"/>
  <ellipse cx="21" cy="16" rx="1.8" ry="2.2" fill="#1a1b26"/>
  <circle cx="21.5" cy="15.3" r="0.6" fill="#fff"/>
  <polygon points="18,19 16.8,20.5 19.2,20.5" fill="#f7768e"/>
  <path d="M16.8,20.5 Q18,22 19.2,20.5" stroke="#c0caf5" stroke-width="0.6" fill="none"/>
  <line x1="10" y1="19.5" x2="16" y2="20" stroke="#c0caf5" stroke-width="0.5" opacity="0.7"/>
  <line x1="10" y1="21" x2="16" y2="20.8" stroke="#c0caf5" stroke-width="0.5" opacity="0.7"/>
  <line x1="26" y1="19.5" x2="20" y2="20" stroke="#c0caf5" stroke-width="0.5" opacity="0.7"/>
  <line x1="26" y1="21" x2="20" y2="20.8" stroke="#c0caf5" stroke-width="0.5" opacity="0.7"/>
  <path d="M27,28 Q33,24 31,20 Q30,17 28,19" stroke="#a9b1d6" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <ellipse cx="14" cy="32" rx="3" ry="1.8" fill="#a9b1d6"/>
  <ellipse cx="22" cy="32" rx="3" ry="1.8" fill="#a9b1d6"/>
</svg>"""
```

- [ ] **Step 3: conftest.py 작성** (pytest import 경로 설정)

```python
# conftest.py  (week4/neural_network_visualizer_pyside6/conftest.py)
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
```

- [ ] **Step 4: Commit**

```bash
git add week4/neural_network_visualizer_pyside6/
git commit -m "feat: week4 NN visualizer — project skeleton + colors"
```

---

## Task 2: shared/matplotlib_canvas.py

**Files:**
- Create: `week4/neural_network_visualizer_pyside6/shared/matplotlib_canvas.py`
- Create: `week4/neural_network_visualizer_pyside6/tests/test_models.py` (첫 스모크 테스트)

- [ ] **Step 1: 테스트 작성**

```python
# tests/test_models.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication(sys.argv)

def test_matplotlib_canvas_creates(app):
    from shared.matplotlib_canvas import MatplotlibCanvas
    c = MatplotlibCanvas()
    assert c.fig is not None
    assert c.ax is not None

def test_matplotlib_canvas_nrows(app):
    from shared.matplotlib_canvas import MatplotlibCanvas
    c = MatplotlibCanvas(nrows=1, ncols=2)
    assert c.axes.shape == (2,)
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
.venv/Scripts/python.exe -m pytest week4/neural_network_visualizer_pyside6/tests/test_models.py -v
```
Expected: `ImportError: No module named 'shared.matplotlib_canvas'`

- [ ] **Step 3: matplotlib_canvas.py 작성**

```python
# shared/matplotlib_canvas.py
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout
from .colors import COLORS


class MatplotlibCanvas(QWidget):
    def __init__(self, nrows=1, ncols=1, parent=None):
        super().__init__(parent)
        self.fig = Figure(facecolor=COLORS["card"])
        self.canvas = FigureCanvasQTAgg(self.fig)
        if nrows == 1 and ncols == 1:
            self.ax = self.fig.add_subplot(1, 1, 1)
            self.axes = self.ax
        else:
            self.axes = self.fig.subplots(nrows, ncols)
            self.ax = self.axes[0]
        self._apply_dark_all()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def _apply_dark_all(self):
        import numpy as np
        axes_flat = np.array(self.axes).flatten() if hasattr(self.axes, '__iter__') else [self.axes]
        for ax in axes_flat:
            self._style_ax(ax)

    @staticmethod
    def _style_ax(ax):
        ax.set_facecolor(COLORS["bg"])
        ax.tick_params(colors=COLORS["text_muted"], labelsize=8)
        ax.xaxis.label.set_color(COLORS["text_dim"])
        ax.yaxis.label.set_color(COLORS["text_dim"])
        for spine in ax.spines.values():
            spine.set_edgecolor(COLORS["border"])
        ax.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.5)

    def clear(self):
        import numpy as np
        axes_flat = np.array(self.axes).flatten() if hasattr(self.axes, '__iter__') else [self.axes]
        for ax in axes_flat:
            ax.cla()
        self._apply_dark_all()

    def draw(self):
        self.canvas.draw_idle()
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
.venv/Scripts/python.exe -m pytest week4/neural_network_visualizer_pyside6/tests/test_models.py -v
```
Expected: 2 PASSED

- [ ] **Step 5: Commit**

```bash
git add week4/neural_network_visualizer_pyside6/shared/matplotlib_canvas.py week4/neural_network_visualizer_pyside6/tests/
git commit -m "feat: MatplotlibCanvas dark-theme wrapper"
```

---

## Task 3: shared/train_worker.py

**Files:**
- Create: `week4/neural_network_visualizer_pyside6/shared/train_worker.py`
- Create: `week4/neural_network_visualizer_pyside6/tests/test_train_worker.py`

- [ ] **Step 1: 테스트 작성**

```python
# tests/test_train_worker.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication(sys.argv)

def _make_tiny_model():
    import tensorflow as tf
    m = tf.keras.Sequential([
        tf.keras.layers.Dense(4, activation="relu", input_shape=(1,)),
        tf.keras.layers.Dense(1),
    ])
    m.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return m

def test_worker_emits_epoch_done(app, qtbot):
    from shared.train_worker import TrainWorker
    x = np.linspace(0, 1, 20).reshape(-1, 1).astype(np.float32)
    y = x * 2
    worker = TrainWorker(_make_tiny_model(), x, y, epochs=3, val_split=0.1)
    epochs_received = []
    worker.epoch_done.connect(lambda ep, logs: epochs_received.append(ep))
    with qtbot.waitSignal(worker.train_done, timeout=30000):
        worker.start()
    assert len(epochs_received) == 3

def test_worker_stop_flag(app, qtbot):
    from shared.train_worker import TrainWorker
    x = np.linspace(0, 1, 50).reshape(-1, 1).astype(np.float32)
    y = x * 2
    worker = TrainWorker(_make_tiny_model(), x, y, epochs=100, val_split=0.1)
    epochs_received = []
    worker.epoch_done.connect(lambda ep, logs: epochs_received.append(ep))
    def stop_early():
        worker.stop()
    QTimer.singleShot(500, stop_early)
    with qtbot.waitSignal(worker.train_done, timeout=15000):
        worker.start()
    assert len(epochs_received) < 100
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
.venv/Scripts/python.exe -m pytest week4/neural_network_visualizer_pyside6/tests/test_train_worker.py -v
```
Expected: `ImportError: No module named 'shared.train_worker'`

- [ ] **Step 3: train_worker.py 작성**

```python
# shared/train_worker.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from PySide6.QtCore import QThread, Signal
import numpy as np


class TrainWorker(QThread):
    epoch_done = Signal(int, dict)   # (epoch_index, logs_dict)
    train_done = Signal(object)      # keras History object
    train_error = Signal(str)        # error message string

    def __init__(self, model, x_train, y_train, epochs: int,
                 val_split: float = 0.1, parent=None):
        super().__init__(parent)
        self._model = model
        self._x = x_train
        self._y = y_train
        self._epochs = epochs
        self._val_split = val_split
        self.stop_flag = False

    def run(self):
        import tensorflow as tf

        worker_ref = self

        class _Callback(tf.keras.callbacks.Callback):
            def on_epoch_end(self, epoch, logs=None):
                worker_ref.epoch_done.emit(epoch, dict(logs or {}))
                if worker_ref.stop_flag:
                    self.model.stop_training = True

        try:
            history = self._model.fit(
                self._x, self._y,
                epochs=self._epochs,
                validation_split=self._val_split,
                callbacks=[_Callback()],
                verbose=0,
            )
            self.train_done.emit(history)
        except Exception as exc:
            self.train_error.emit(str(exc))

    def stop(self):
        self.stop_flag = True
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
.venv/Scripts/python.exe -m pytest week4/neural_network_visualizer_pyside6/tests/test_train_worker.py -v
```
Expected: 2 PASSED

- [ ] **Step 5: Commit**

```bash
git add week4/neural_network_visualizer_pyside6/shared/train_worker.py week4/neural_network_visualizer_pyside6/tests/test_train_worker.py
git commit -m "feat: QThread TrainWorker with stop_flag + epoch_done signal"
```

---

## Task 4: shared/base_lab_window.py

**Files:**
- Create: `week4/neural_network_visualizer_pyside6/shared/base_lab_window.py`

- [ ] **Step 1: base_lab_window.py 작성**

```python
# shared/base_lab_window.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QPushButton, QProgressBar,
    QLineEdit, QComboBox, QGraphicsOpacityEffect,
)
from PySide6.QtCore import Qt, QTimer, QByteArray
from PySide6.QtSvgWidgets import QSvgWidget
from .colors import COLORS, CAT_SVG
from .train_worker import TrainWorker
from .matplotlib_canvas import MatplotlibCanvas


class BaseLabWindow(QMainWindow):
    DEFAULT_PARAMS = {
        "layers": "[64, 64]",
        "activation": "relu",
        "epochs": 500,
        "lr": 0.001,
    }

    def __init__(self, title: str, footer_text: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(1100, 680)
        self._worker: TrainWorker | None = None
        self._current_model = None
        self._total_epochs = self.DEFAULT_PARAMS["epochs"]
        self._loss_history: dict = {"loss": [], "val_loss": []}
        self._build_ui(title, footer_text)
        QTimer.singleShot(300, self._on_train_clicked)

    # ── UI Construction ──────────────────────────────────────────────

    def _build_ui(self, title: str, footer_text: str):
        self.setStyleSheet(f"QMainWindow, QWidget {{ background: {COLORS['bg']}; }}")
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        root.addWidget(self._make_header(title))

        body = QWidget()
        hbox = QHBoxLayout(body)
        hbox.setContentsMargins(12, 10, 12, 10)
        hbox.setSpacing(8)
        root.addWidget(body, stretch=1)

        hbox.addWidget(self._make_left_panel())
        center_card = self._make_card()
        cl = QVBoxLayout(center_card)
        cl.setContentsMargins(6, 6, 6, 6)
        self.main_canvas = self._build_main_chart()
        cl.addWidget(self.main_canvas)
        hbox.addWidget(center_card, stretch=1)
        hbox.addWidget(self._make_right_panel())

        root.addWidget(self._make_footer(footer_text))

    def _make_header(self, title: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {COLORS['panel']}; border-bottom: 1px solid {COLORS['border']};")
        h = QHBoxLayout(w)
        h.setContentsMargins(14, 8, 14, 8)
        lbl = QLabel(f"{title}  |  MIT 6.S191 Week 4")
        lbl.setStyleSheet(f"color: {COLORS['accent']}; font-size: 13px; font-weight: bold; background: transparent;")
        h.addWidget(lbl)
        h.addStretch()
        cat = QSvgWidget()
        cat.load(QByteArray(CAT_SVG))
        cat.setFixedSize(36, 36)
        cat.setStyleSheet("background: transparent;")
        fx = QGraphicsOpacityEffect(cat)
        fx.setOpacity(0.85)
        cat.setGraphicsEffect(fx)
        h.addWidget(cat)
        return w

    def _make_footer(self, text: str) -> QLabel:
        lbl = QLabel(text or "PySide6 · TensorFlow/Keras · Matplotlib")
        lbl.setStyleSheet(
            f"background: {COLORS['panel']}; color: {COLORS['text_muted']}; "
            f"font-size: 10px; padding: 5px 12px; "
            f"border-top: 1px solid {COLORS['border']};"
        )
        return lbl

    def _make_card(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['panel']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        return f

    def _make_left_panel(self) -> QFrame:
        card = self._make_card()
        card.setFixedWidth(215)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        self._add_section_label(layout, "⚙  Parameters")
        for field, key in [("Hidden Layers", "layers"), ("Epochs", "epochs"), ("Learning Rate", "lr")]:
            self._add_field_label(layout, field)
            inp = QLineEdit(str(self.DEFAULT_PARAMS[key]))
            inp.setStyleSheet(self._input_qss())
            layout.addWidget(inp)
            setattr(self, f"_inp_{field.lower().replace(' ', '_')}", inp)

        self._add_field_label(layout, "Activation")
        self._inp_activation = QComboBox()
        self._inp_activation.addItems(["relu", "tanh", "sigmoid", "elu"])
        self._inp_activation.setCurrentText(str(self.DEFAULT_PARAMS["activation"]))
        self._inp_activation.setStyleSheet(self._combo_qss())
        layout.addWidget(self._inp_activation)

        custom = self._build_custom_controls()
        if custom is not None:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet(f"color: {COLORS['border']}; background: {COLORS['border']}; max-height: 1px;")
            layout.addWidget(sep)
            layout.addWidget(custom)

        layout.addStretch()

        for label, color, attr in [
            ("▶  Train", COLORS["accent"], "_btn_train"),
            ("⏹  Stop",  COLORS["danger"], "_btn_stop"),
            ("↺  Reset", COLORS["card"],   "_btn_reset"),
        ]:
            btn = QPushButton(label)
            tc = COLORS["bg"] if attr != "_btn_reset" else COLORS["text_dim"]
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color}; color: {tc};
                    border: none; border-radius: 4px;
                    padding: 6px; font-size: 11px; font-weight: bold;
                }}
                QPushButton:disabled {{ opacity: 0.4; }}
            """)
            layout.addWidget(btn)
            setattr(self, attr, btn)

        self._btn_train.clicked.connect(self._on_train_clicked)
        self._btn_stop.clicked.connect(self._on_stop_clicked)
        self._btn_reset.clicked.connect(self._on_reset_clicked)
        self._btn_stop.setEnabled(False)

        self._epoch_bar = QProgressBar()
        self._epoch_bar.setRange(0, 100)
        self._epoch_bar.setValue(0)
        self._epoch_bar.setTextVisible(False)
        self._epoch_bar.setFixedHeight(6)
        self._epoch_bar.setStyleSheet(f"""
            QProgressBar {{ background: {COLORS['card']}; border-radius: 3px; border: none; }}
            QProgressBar::chunk {{ background: {COLORS['success']}; border-radius: 3px; }}
        """)
        layout.addWidget(self._epoch_bar)

        self._epoch_label = QLabel("Ready")
        self._epoch_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; background: transparent;")
        layout.addWidget(self._epoch_label)

        return card

    def _make_right_panel(self) -> QFrame:
        card = self._make_card()
        card.setFixedWidth(175)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        self._add_section_label(layout, "📊  Training")
        self._stat_labels: dict[str, QLabel] = {}
        for key, color in [("Train Loss", COLORS["danger"]), ("Val Loss", COLORS["accent"]), ("MAE", COLORS["success"])]:
            self._add_field_label(layout, key)
            v = QLabel("—")
            v.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px; background: transparent;")
            layout.addWidget(v)
            self._stat_labels[key] = v

        self.loss_canvas = MatplotlibCanvas(nrows=1, ncols=1)
        self.loss_canvas.setFixedHeight(90)
        layout.addWidget(self.loss_canvas)

        custom_info = self._build_custom_info()
        if custom_info is not None:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet(f"color: {COLORS['border']}; background: {COLORS['border']}; max-height: 1px;")
            layout.addWidget(sep)
            layout.addWidget(custom_info)

        layout.addStretch()
        return card

    # ── Style helpers ────────────────────────────────────────────────

    def _add_section_label(self, layout, text: str):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {COLORS['accent']}; font-weight: bold; font-size: 12px; background: transparent;")
        layout.addWidget(lbl)

    def _add_field_label(self, layout, text: str):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px; background: transparent;")
        layout.addWidget(lbl)

    def _input_qss(self) -> str:
        return f"""
            QLineEdit {{
                background: {COLORS['card']}; color: {COLORS['text']};
                border: 1px solid {COLORS['border_light']}; border-radius: 4px;
                padding: 4px 6px; font-size: 11px;
            }}
        """

    def _combo_qss(self) -> str:
        return f"""
            QComboBox {{
                background: {COLORS['card']}; color: {COLORS['text']};
                border: 1px solid {COLORS['border_light']}; border-radius: 4px;
                padding: 4px 6px; font-size: 11px;
            }}
            QComboBox QAbstractItemView {{
                background: {COLORS['card']}; color: {COLORS['text']};
                selection-background-color: {COLORS['accent']};
            }}
        """

    # ── Abstract interface (subclasses implement) ────────────────────

    def _build_custom_controls(self) -> QWidget | None:
        return None

    def _build_main_chart(self) -> QWidget:
        raise NotImplementedError("Subclass must implement _build_main_chart()")

    def _build_custom_info(self) -> QWidget | None:
        return None

    def _get_model_and_data(self) -> tuple:
        """Return (keras.Model, x_train: ndarray, y_train: ndarray)."""
        raise NotImplementedError("Subclass must implement _get_model_and_data()")

    def _on_train_complete(self, history):
        """Called when training finishes. Override to update main chart."""
        self._epoch_label.setText("Done ✓")
        self._btn_train.setEnabled(True)
        self._btn_stop.setEnabled(False)

    def _reset_custom(self):
        """Hook for subclasses to reset their own state on Reset."""
        pass

    # ── Slot handlers ────────────────────────────────────────────────

    def _on_epoch_done(self, epoch: int, logs: dict):
        pct = int((epoch + 1) / self._total_epochs * 100)
        self._epoch_bar.setValue(pct)
        self._epoch_label.setText(f"Epoch {epoch + 1} / {self._total_epochs}")

        loss = logs.get("loss", 0.0)
        val_loss = logs.get("val_loss", 0.0)
        mae = logs.get("mae", logs.get("mean_absolute_error", 0.0))
        self._stat_labels["Train Loss"].setText(f"{loss:.5f}")
        self._stat_labels["Val Loss"].setText(f"{val_loss:.5f}")
        self._stat_labels["MAE"].setText(f"{mae:.4f}")

        self._loss_history["loss"].append(loss)
        self._loss_history["val_loss"].append(val_loss)
        ax = self.loss_canvas.ax
        ax.cla()
        ax.set_facecolor(COLORS["bg"])
        ax.plot(self._loss_history["loss"], color=COLORS["danger"], linewidth=1)
        ax.plot(self._loss_history["val_loss"], color=COLORS["accent"], linewidth=1)
        ax.tick_params(labelsize=7, colors=COLORS["text_muted"])
        for sp in ax.spines.values():
            sp.set_edgecolor(COLORS["border"])
        self.loss_canvas.draw()

    def _on_train_clicked(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()

        self._loss_history = {"loss": [], "val_loss": []}
        self._epoch_bar.setValue(0)

        try:
            model, x_train, y_train = self._get_model_and_data()
        except Exception as exc:
            self._epoch_label.setText(f"Error: {exc}")
            return

        self._current_model = model
        self._total_epochs = int(self._inp_epochs.text())

        self._worker = TrainWorker(model, x_train, y_train,
                                   self._total_epochs, val_split=0.1)
        self._worker.epoch_done.connect(self._on_epoch_done)
        self._worker.train_done.connect(self._on_train_complete)
        self._worker.train_error.connect(
            lambda e: self._epoch_label.setText(f"Error: {e}")
        )
        self._worker.start()
        self._btn_train.setEnabled(False)
        self._btn_stop.setEnabled(True)
        self._epoch_label.setText("Training…")

    def _on_stop_clicked(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
        self._btn_train.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._epoch_label.setText("Stopped")

    def _on_reset_clicked(self):
        self._on_stop_clicked()
        self._inp_hidden_layers.setText(str(self.DEFAULT_PARAMS["layers"]))
        self._inp_epochs.setText(str(self.DEFAULT_PARAMS["epochs"]))
        self._inp_learning_rate.setText(str(self.DEFAULT_PARAMS["lr"]))
        self._inp_activation.setCurrentText(str(self.DEFAULT_PARAMS["activation"]))
        for lbl in self._stat_labels.values():
            lbl.setText("—")
        self._epoch_bar.setValue(0)
        self._epoch_label.setText("Ready")
        self._loss_history = {"loss": [], "val_loss": []}
        self.loss_canvas.clear()
        self.loss_canvas.draw()
        self._reset_custom()

    # ── Helpers ──────────────────────────────────────────────────────

    def _parse_layers(self) -> list[int]:
        import ast
        text = self._inp_hidden_layers.text().strip()
        result = ast.literal_eval(text)
        return [result] if isinstance(result, int) else list(result)

    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()
        super().closeEvent(event)
```

- [ ] **Step 2: 스모크 테스트 추가** (`tests/test_models.py` 하단에 추가)

```python
def test_base_lab_window_raises_without_subclass(app):
    """_build_main_chart / _get_model_and_data 미구현 시 NotImplementedError."""
    from shared.base_lab_window import BaseLabWindow
    import pytest
    with pytest.raises(NotImplementedError):
        # BaseLabWindow directly calls _build_main_chart in __init__
        BaseLabWindow("Test")
```

- [ ] **Step 3: 테스트 통과 확인**

```bash
.venv/Scripts/python.exe -m pytest week4/neural_network_visualizer_pyside6/tests/test_models.py::test_base_lab_window_raises_without_subclass -v
```
Expected: PASSED

- [ ] **Step 4: Commit**

```bash
git add week4/neural_network_visualizer_pyside6/shared/base_lab_window.py
git commit -m "feat: BaseLabWindow — 3-panel dark layout, QThread wiring, cat SVG"
```

---

## Task 5: 런처 (lab_card.py + launcher_window.py + main.py)

**Files:**
- Create: `week4/neural_network_visualizer_pyside6/launcher/lab_card.py`
- Create: `week4/neural_network_visualizer_pyside6/launcher/launcher_window.py`
- Create: `week4/neural_network_visualizer_pyside6/main.py`
- Create: `week4/neural_network_visualizer_pyside6/tests/test_plugin_discovery.py`

- [ ] **Step 1: 플러그인 발견 테스트 작성**

```python
# tests/test_plugin_discovery.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_discover_labs_finds_four():
    from launcher.launcher_window import discover_labs
    labs = discover_labs()
    assert len(labs) == 4

def test_discover_labs_have_required_keys():
    from launcher.launcher_window import discover_labs
    for meta in discover_labs():
        assert "id" in meta
        assert "title" in meta
        assert "icon" in meta
        assert "description" in meta
        assert "window_class" in meta
```

Expected: FAIL (no module yet)

- [ ] **Step 2: lab_card.py 작성**

```python
# launcher/lab_card.py
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal
from shared.colors import COLORS


class LabCard(QFrame):
    open_requested = Signal(str)   # emits window_class path

    def __init__(self, meta: dict, parent=None):
        super().__init__(parent)
        self._meta = meta
        self.setFixedSize(200, 160)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QFrame:hover {{
                border: 1px solid {COLORS['accent']};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(4)

        icon = QLabel(meta["icon"])
        icon.setStyleSheet(f"font-size: 28px; background: transparent; border: none;")
        layout.addWidget(icon)

        title = QLabel(meta["title"])
        title.setStyleSheet(f"color: {COLORS['text']}; font-weight: bold; font-size: 12px; background: transparent; border: none;")
        title.setWordWrap(True)
        layout.addWidget(title)

        desc = QLabel(meta["description"])
        desc.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; background: transparent; border: none;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        btn = QPushButton("열기")
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']}; color: {COLORS['bg']};
                border: none; border-radius: 4px;
                padding: 5px; font-size: 11px; font-weight: bold;
            }}
        """)
        btn.clicked.connect(lambda: self.open_requested.emit(meta["window_class"]))
        layout.addWidget(btn)
```

- [ ] **Step 3: launcher_window.py 작성**

```python
# launcher/launcher_window.py
import sys
import glob
import importlib
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QLabel
)
from PySide6.QtCore import QByteArray
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QHBoxLayout, QGraphicsOpacityEffect
from shared.colors import COLORS, CAT_SVG
from .lab_card import LabCard


def discover_labs() -> list[dict]:
    """Scan labs/lab*/lab_meta.py and return list of LAB_META dicts, sorted by id."""
    base = os.path.join(os.path.dirname(__file__), "..", "labs")
    pattern = os.path.join(base, "lab*", "lab_meta.py")
    metas = []
    for path in sorted(glob.glob(pattern)):
        parts = path.replace("\\", "/").split("/")
        lab_dir = parts[-2]           # e.g. "lab1_function"
        module_name = f"labs.{lab_dir}.lab_meta"
        mod = importlib.import_module(module_name)
        metas.append(mod.LAB_META)
    return metas


class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Week 4 · Neural Network Visualizer")
        self.setMinimumSize(520, 460)
        self._open_windows: dict[str, object] = {}
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"QMainWindow, QWidget {{ background: {COLORS['bg']}; }}")
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QWidget()
        header.setStyleSheet(f"background: {COLORS['panel']}; border-bottom: 1px solid {COLORS['border']};")
        hh = QHBoxLayout(header)
        hh.setContentsMargins(16, 10, 16, 10)
        title = QLabel("Week 4 · Neural Network Visualizer  |  MIT 6.S191")
        title.setStyleSheet(f"color: {COLORS['accent']}; font-size: 14px; font-weight: bold; background: transparent;")
        hh.addWidget(title)
        hh.addStretch()
        cat = QSvgWidget()
        cat.load(QByteArray(CAT_SVG))
        cat.setFixedSize(36, 36)
        cat.setStyleSheet("background: transparent;")
        fx = QGraphicsOpacityEffect(cat)
        fx.setOpacity(0.85)
        cat.setGraphicsEffect(fx)
        hh.addWidget(cat)
        root.addWidget(header)

        # Card grid
        body = QWidget()
        body.setStyleSheet(f"background: {COLORS['bg']};")
        grid = QGridLayout(body)
        grid.setContentsMargins(20, 20, 20, 20)
        grid.setSpacing(14)
        root.addWidget(body, stretch=1)

        metas = discover_labs()
        for i, meta in enumerate(metas):
            card = LabCard(meta)
            card.open_requested.connect(self._open_lab)
            grid.addWidget(card, i // 2, i % 2)

        # Footer
        footer = QLabel("PySide6 · TensorFlow/Keras · MIT 6.S191 Week 4")
        footer.setStyleSheet(
            f"background: {COLORS['panel']}; color: {COLORS['text_muted']}; "
            f"font-size: 10px; padding: 5px 16px; border-top: 1px solid {COLORS['border']};"
        )
        root.addWidget(footer)

    def _open_lab(self, window_class_path: str):
        if window_class_path in self._open_windows:
            w = self._open_windows[window_class_path]
            w.raise_()
            w.activateWindow()
            return
        module_path, cls_name = window_class_path.rsplit(".", 1)
        mod = importlib.import_module(module_path)
        cls = getattr(mod, cls_name)
        win = cls()
        win.setAttribute(win.WA_DeleteOnClose if hasattr(win, 'WA_DeleteOnClose') else 55)
        win.destroyed.connect(lambda: self._open_windows.pop(window_class_path, None))
        self._open_windows[window_class_path] = win
        win.show()
```

- [ ] **Step 4: main.py 작성**

```python
# main.py
import sys
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Ensure the package root is on the path when running as a script
sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from launcher.launcher_window import LauncherWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Week4 NN Visualizer")
    win = LauncherWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: 테스트 — 아직 lab_meta.py 없으니 0개 발견 확인**

```bash
.venv/Scripts/python.exe -m pytest week4/neural_network_visualizer_pyside6/tests/test_plugin_discovery.py -v
```
Expected: `assert 0 == 4` — 나중에 모든 Lab 추가 후 다시 통과

- [ ] **Step 6: Commit**

```bash
git add week4/neural_network_visualizer_pyside6/launcher/ week4/neural_network_visualizer_pyside6/main.py
git commit -m "feat: Launcher — plugin discovery + LabCard grid + main.py"
```

---

## Task 6: Lab 1 — 함수 근사

**Files:**
- Create: `week4/neural_network_visualizer_pyside6/labs/lab1_function/lab_meta.py`
- Create: `week4/neural_network_visualizer_pyside6/labs/lab1_function/model.py`
- Create: `week4/neural_network_visualizer_pyside6/labs/lab1_function/window.py`

- [ ] **Step 1: 모델 테스트 추가** (`tests/test_models.py` 하단에 추가)

```python
def test_lab1_make_data_shape():
    from labs.lab1_function.model import make_data
    x_tr, y_tr, x_plot, y_true = make_data("sin(x)")
    assert x_tr.shape == (300, 1)
    assert y_tr.shape == (300, 1)
    assert x_plot.shape == (300,)
    assert y_true.shape == (300,)

def test_lab1_make_model_output_shape():
    from labs.lab1_function.model import make_model
    import numpy as np
    m = make_model([32, 16], "relu", 0.001)
    out = m.predict(np.zeros((5, 1), dtype="float32"), verbose=0)
    assert out.shape == (5, 1)
```

- [ ] **Step 2: lab_meta.py 작성**

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

- [ ] **Step 3: model.py 작성**

```python
# labs/lab1_function/model.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import numpy as np
import tensorflow as tf
from tensorflow import keras

FUNCTIONS = {
    "sin(x)":           lambda x: np.sin(x),
    "cos(x)+0.5sin(2x)": lambda x: np.cos(x) + 0.5 * np.sin(2 * x),
    "x·sin(x)":         lambda x: x * np.sin(x),
}
X_LO, X_HI, N = -2 * np.pi, 2 * np.pi, 300


def make_data(func_name: str):
    x = np.linspace(X_LO, X_HI, N)
    idx = np.random.permutation(N)
    xs, ys = x[idx], FUNCTIONS[func_name](x[idx])
    return (
        xs.reshape(-1, 1).astype(np.float32),
        ys.reshape(-1, 1).astype(np.float32),
        x,
        FUNCTIONS[func_name](x),
    )


def make_model(layers: list[int], activation: str, lr: float) -> keras.Model:
    model = keras.Sequential()
    model.add(keras.layers.Input(shape=(1,)))
    for units in layers:
        model.add(keras.layers.Dense(units, activation=activation))
    model.add(keras.layers.Dense(1, activation="linear"))
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss="mse",
        metrics=["mae"],
    )
    return model
```

- [ ] **Step 4: window.py 작성**

```python
# labs/lab1_function/window.py
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from shared.base_lab_window import BaseLabWindow
from shared.matplotlib_canvas import MatplotlibCanvas
from shared.colors import COLORS
from .model import FUNCTIONS, make_data, make_model


class Lab1Window(BaseLabWindow):
    DEFAULT_PARAMS = {
        "layers": "[128, 128, 64]",
        "activation": "tanh",
        "epochs": 1000,
        "lr": 0.001,
    }

    def __init__(self, parent=None):
        self._x_plot = np.array([])
        self._y_true = np.array([])
        super().__init__(
            title="Lab 1 · 함수 근사",
            footer_text="Layers=[128,128,64] · tanh · 1000 epochs · x∈[-2π, 2π]",
            parent=parent,
        )

    def _build_custom_controls(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._add_section_label(layout, "🎯  Lab Controls")
        self._add_field_label(layout, "Function")
        self._fn_combo = QComboBox()
        self._fn_combo.addItems(list(FUNCTIONS.keys()))
        self._fn_combo.setStyleSheet(self._combo_qss())
        layout.addWidget(self._fn_combo)
        return w

    def _build_main_chart(self) -> QWidget:
        self._main_canvas = MatplotlibCanvas(nrows=1, ncols=1)
        return self._main_canvas

    def _build_custom_info(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._add_section_label(layout, "🔬  Results")
        self._result_labels: dict[str, QLabel] = {}
        for key in ["MSE", "R²"]:
            self._add_field_label(layout, key)
            v = QLabel("—")
            v.setStyleSheet(f"color: {COLORS['highlight']}; font-weight: bold; font-size: 12px; background: transparent;")
            layout.addWidget(v)
            self._result_labels[key] = v
        return w

    def _get_model_and_data(self) -> tuple:
        fn = self._fn_combo.currentText()
        x_tr, y_tr, self._x_plot, self._y_true = make_data(fn)
        model = make_model(self._parse_layers(),
                           self._inp_activation.currentText(),
                           float(self._inp_learning_rate.text()))
        return model, x_tr, y_tr

    def _on_train_complete(self, history):
        super()._on_train_complete(history)
        if self._current_model is None:
            return
        x_in = self._x_plot.reshape(-1, 1).astype(np.float32)
        y_pred = self._current_model.predict(x_in, verbose=0).flatten()

        mse = float(np.mean((self._y_true - y_pred) ** 2))
        ss_res = float(np.sum((self._y_true - y_pred) ** 2))
        ss_tot = float(np.sum((self._y_true - np.mean(self._y_true)) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
        self._result_labels["MSE"].setText(f"{mse:.6f}")
        self._result_labels["R²"].setText(f"{r2:.4f}")

        ax = self._main_canvas.ax
        ax.cla()
        ax.set_facecolor(COLORS["bg"])
        ax.plot(self._x_plot, self._y_true,
                color=COLORS["accent"], linewidth=2, label="True", alpha=0.8)
        ax.plot(self._x_plot, y_pred,
                color=COLORS["danger"], linewidth=1.5, linestyle="--", label="Predicted")
        ax.legend(facecolor=COLORS["card"], edgecolor=COLORS["border"],
                  labelcolor=COLORS["text_dim"], fontsize=9)
        ax.set_title(f"{self._fn_combo.currentText()}", color=COLORS["text_dim"], fontsize=10)
        for sp in ax.spines.values():
            sp.set_edgecolor(COLORS["border"])
        ax.tick_params(colors=COLORS["text_muted"])
        ax.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.5)
        self._main_canvas.draw()
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
.venv/Scripts/python.exe -m pytest week4/neural_network_visualizer_pyside6/tests/test_models.py -v
```
Expected: 5 PASSED (2 기존 + 2 lab1 신규 + 1 base 스모크)

- [ ] **Step 6: Commit**

```bash
git add week4/neural_network_visualizer_pyside6/labs/lab1_function/
git commit -m "feat: Lab1 — function approximation (sin/cos/x·sin)"
```

---

## Task 7: Lab 2 — 포물선 회귀

**Files:**
- Create: `week4/neural_network_visualizer_pyside6/labs/lab2_projectile/lab_meta.py`
- Create: `week4/neural_network_visualizer_pyside6/labs/lab2_projectile/model.py`
- Create: `week4/neural_network_visualizer_pyside6/labs/lab2_projectile/window.py`

- [ ] **Step 1: 모델 테스트 추가** (`tests/test_models.py` 하단)

```python
def test_lab2_make_data_shape():
    from labs.lab2_projectile.model import make_data
    X, Y = make_data()
    assert X.shape == (2000, 3)
    assert Y.shape == (2000, 2)

def test_lab2_true_trajectory_shape():
    from labs.lab2_projectile.model import true_trajectory
    t, x, y = true_trajectory(v0=30.0, theta_deg=45.0)
    assert len(t) == len(x) == len(y) == 100
    assert float(y[0]) == pytest.approx(0.0, abs=0.01)
```

- [ ] **Step 2: lab_meta.py 작성**

```python
# labs/lab2_projectile/lab_meta.py
LAB_META = {
    "id": "lab2_projectile",
    "title": "Lab 2 · 포물선 회귀",
    "icon": "🚀",
    "description": "2D Regression — Physics",
    "window_class": "labs.lab2_projectile.window.Lab2Window",
}
```

- [ ] **Step 3: model.py 작성**

```python
# labs/lab2_projectile/model.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import numpy as np
import tensorflow as tf
from tensorflow import keras

G = 9.8
N_SAMPLES = 2000


def make_data():
    rng = np.random.default_rng(42)
    v0 = rng.uniform(10, 50, N_SAMPLES)
    theta = rng.uniform(10, 80, N_SAMPLES)
    t_max = 2 * v0 * np.sin(np.radians(theta)) / G
    t = rng.uniform(0, 1, N_SAMPLES) * t_max
    x = v0 * np.cos(np.radians(theta)) * t + rng.normal(0, 0.05, N_SAMPLES)
    y = (v0 * np.sin(np.radians(theta)) * t
         - 0.5 * G * t ** 2
         + rng.normal(0, 0.05, N_SAMPLES))
    X = np.stack([v0, theta, t], axis=1).astype(np.float32)
    Y = np.stack([x, y], axis=1).astype(np.float32)
    return X, Y


def make_model(layers: list[int], activation: str, lr: float) -> keras.Model:
    model = keras.Sequential()
    model.add(keras.layers.Input(shape=(3,)))
    for units in layers:
        model.add(keras.layers.Dense(units, activation=activation))
        model.add(keras.layers.Dropout(0.1))
    model.add(keras.layers.Dense(2, activation="linear"))
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss="mse",
        metrics=["mae"],
    )
    return model


def true_trajectory(v0: float, theta_deg: float, n_points: int = 100):
    theta = np.radians(theta_deg)
    t_flight = 2 * v0 * np.sin(theta) / G
    t = np.linspace(0, t_flight, n_points)
    x = v0 * np.cos(theta) * t
    y = v0 * np.sin(theta) * t - 0.5 * G * t ** 2
    return t, x, y
```

- [ ] **Step 4: window.py 작성**

```python
# labs/lab2_projectile/window.py
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt
from shared.base_lab_window import BaseLabWindow
from shared.matplotlib_canvas import MatplotlibCanvas
from shared.colors import COLORS
from .model import make_data, make_model, true_trajectory


class Lab2Window(BaseLabWindow):
    DEFAULT_PARAMS = {
        "layers": "[128, 64, 32]",
        "activation": "relu",
        "epochs": 500,
        "lr": 0.001,
    }

    def __init__(self, parent=None):
        self._x_train, self._y_train = make_data()
        super().__init__(
            title="Lab 2 · 포물선 회귀",
            footer_text="Input: (v₀, θ, t) → Output: (x, y) · Dropout 0.1 · 500 epochs",
            parent=parent,
        )

    def _build_custom_controls(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._add_section_label(layout, "🎯  Trajectory Test")

        self._v0_lbl = QLabel("v₀ (m/s): 30")
        self._v0_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px; background: transparent;")
        layout.addWidget(self._v0_lbl)
        self._v0_slider = QSlider(Qt.Orientation.Horizontal)
        self._v0_slider.setRange(10, 50)
        self._v0_slider.setValue(30)
        self._v0_slider.valueChanged.connect(self._on_v0_changed)
        layout.addWidget(self._v0_slider)

        self._theta_lbl = QLabel("θ (°): 45")
        self._theta_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px; background: transparent;")
        layout.addWidget(self._theta_lbl)
        self._theta_slider = QSlider(Qt.Orientation.Horizontal)
        self._theta_slider.setRange(10, 80)
        self._theta_slider.setValue(45)
        self._theta_slider.valueChanged.connect(self._on_theta_changed)
        layout.addWidget(self._theta_slider)
        return w

    def _build_main_chart(self) -> QWidget:
        self._main_canvas = MatplotlibCanvas(nrows=1, ncols=1)
        return self._main_canvas

    def _build_custom_info(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._add_section_label(layout, "🔬  Error")
        self._err_labels: dict[str, QLabel] = {}
        for key in ["Height Err (m)", "Range Err (m)"]:
            self._add_field_label(layout, key)
            v = QLabel("—")
            v.setStyleSheet(f"color: {COLORS['highlight']}; font-weight: bold; font-size: 12px; background: transparent;")
            layout.addWidget(v)
            self._err_labels[key] = v
        return w

    def _get_model_and_data(self) -> tuple:
        model = make_model(self._parse_layers(),
                           self._inp_activation.currentText(),
                           float(self._inp_learning_rate.text()))
        return model, self._x_train, self._y_train

    def _on_train_complete(self, history):
        super()._on_train_complete(history)
        self._update_chart()

    def _on_v0_changed(self, v: int):
        self._v0_lbl.setText(f"v₀ (m/s): {v}")
        self._update_chart()

    def _on_theta_changed(self, v: int):
        self._theta_lbl.setText(f"θ (°): {v}")
        self._update_chart()

    def _update_chart(self):
        if self._current_model is None:
            return
        v0 = float(self._v0_slider.value())
        theta = float(self._theta_slider.value())
        t_arr, x_true, y_true = true_trajectory(v0, theta)
        inp = np.stack([
            np.full(len(t_arr), v0),
            np.full(len(t_arr), theta),
            t_arr,
        ], axis=1).astype(np.float32)
        pred = self._current_model.predict(inp, verbose=0)
        x_pred, y_pred = pred[:, 0], pred[:, 1]

        h_true, h_pred = float(np.max(y_true)), float(np.max(y_pred))
        r_true = float(x_true[-1])
        r_pred = float(x_pred[np.argmin(np.abs(y_pred))])
        self._err_labels["Height Err (m)"].setText(f"{abs(h_true - h_pred):.3f}")
        self._err_labels["Range Err (m)"].setText(f"{abs(r_true - r_pred):.3f}")

        ax = self._main_canvas.ax
        ax.cla()
        ax.set_facecolor(COLORS["bg"])
        ax.plot(x_true, y_true, color=COLORS["accent"], linewidth=2,
                label=f"True (v₀={v0:.0f}, θ={theta:.0f}°)", alpha=0.8)
        ax.plot(x_pred, y_pred, color=COLORS["danger"], linewidth=1.5,
                linestyle="--", label="Predicted")
        ax.set_xlabel("x (m)", color=COLORS["text_dim"])
        ax.set_ylabel("y (m)", color=COLORS["text_dim"])
        ax.legend(facecolor=COLORS["card"], edgecolor=COLORS["border"],
                  labelcolor=COLORS["text_dim"], fontsize=9)
        ax.set_title("Projectile Trajectory", color=COLORS["text_dim"], fontsize=10)
        for sp in ax.spines.values():
            sp.set_edgecolor(COLORS["border"])
        ax.tick_params(colors=COLORS["text_muted"])
        ax.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.5)
        self._main_canvas.draw()
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
.venv/Scripts/python.exe -m pytest week4/neural_network_visualizer_pyside6/tests/test_models.py -v
```
Expected: 7 PASSED

- [ ] **Step 6: Commit**

```bash
git add week4/neural_network_visualizer_pyside6/labs/lab2_projectile/
git commit -m "feat: Lab2 — projectile trajectory regression with v0/theta sliders"
```

---

## Task 8: Lab 3 — 과적합 데모

**Files:**
- Create: `week4/neural_network_visualizer_pyside6/labs/lab3_overfitting/lab_meta.py`
- Create: `week4/neural_network_visualizer_pyside6/labs/lab3_overfitting/model.py`
- Create: `week4/neural_network_visualizer_pyside6/labs/lab3_overfitting/window.py`

> **Note:** Lab 3은 3개 모델을 순차 학습하므로 `_on_train_clicked`를 오버라이드한다. 기본 `TrainWorker` 1개가 아닌 state machine (UNDER → GOOD → OVER)으로 동작.

- [ ] **Step 1: 모델 테스트 추가** (`tests/test_models.py` 하단)

```python
def test_lab3_make_data_shape():
    from labs.lab3_overfitting.model import make_data
    x_tr, y_tr, x_plot, y_true = make_data()
    assert x_tr.shape[1] == 1
    assert y_tr.shape[1] == 1

def test_lab3_model_configs():
    from labs.lab3_overfitting.model import MODEL_CONFIGS
    assert "Underfit" in MODEL_CONFIGS
    assert "Good Fit" in MODEL_CONFIGS
    assert "Overfit" in MODEL_CONFIGS
```

- [ ] **Step 2: lab_meta.py 작성**

```python
# labs/lab3_overfitting/lab_meta.py
LAB_META = {
    "id": "lab3_overfitting",
    "title": "Lab 3 · 과적합 데모",
    "icon": "⚖️",
    "description": "Overfitting vs Underfitting",
    "window_class": "labs.lab3_overfitting.window.Lab3Window",
}
```

- [ ] **Step 3: model.py 작성**

```python
# labs/lab3_overfitting/model.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import numpy as np
import tensorflow as tf
from tensorflow import keras

N = 150

MODEL_CONFIGS = {
    "Underfit": {"layers": [4],             "dropout": 0.0},
    "Good Fit": {"layers": [32, 16],        "dropout": 0.2},
    "Overfit":  {"layers": [256, 128, 64, 32], "dropout": 0.0},
}


def make_data():
    rng = np.random.default_rng(0)
    x = np.linspace(-3, 3, N)
    y = np.sin(2 * x) + 0.5 * x + rng.normal(0, 0.3, N)
    idx = rng.permutation(N)
    x, y = x[idx], y[idx]
    return (
        x.reshape(-1, 1).astype(np.float32),
        y.reshape(-1, 1).astype(np.float32),
        np.linspace(-3, 3, 200),
        np.sin(2 * np.linspace(-3, 3, 200)) + 0.5 * np.linspace(-3, 3, 200),
    )


def make_model(config_name: str, lr: float) -> keras.Model:
    cfg = MODEL_CONFIGS[config_name]
    model = keras.Sequential()
    model.add(keras.layers.Input(shape=(1,)))
    for units in cfg["layers"]:
        model.add(keras.layers.Dense(units, activation="relu"))
        if cfg["dropout"] > 0:
            model.add(keras.layers.Dropout(cfg["dropout"]))
    model.add(keras.layers.Dense(1, activation="linear"))
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss="mse",
        metrics=["mae"],
    )
    return model
```

- [ ] **Step 4: window.py 작성**

```python
# labs/lab3_overfitting/window.py
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from shared.base_lab_window import BaseLabWindow
from shared.matplotlib_canvas import MatplotlibCanvas
from shared.train_worker import TrainWorker
from shared.colors import COLORS
from .model import make_data, make_model, MODEL_CONFIGS

_STAGE_ORDER = ["Underfit", "Good Fit", "Overfit"]
_STAGE_COLORS = {
    "Underfit": "#e0af68",
    "Good Fit": "#9ece6a",
    "Overfit":  "#f7768e",
}


class Lab3Window(BaseLabWindow):
    DEFAULT_PARAMS = {
        "layers": "N/A (preset)",
        "activation": "relu",
        "epochs": 200,
        "lr": 0.001,
    }

    def __init__(self, parent=None):
        self._x_tr, self._y_tr, self._x_plot, self._y_true = make_data()
        self._trained: dict[str, np.ndarray] = {}   # name -> y_pred array
        self._stage_idx = 0
        super().__init__(
            title="Lab 3 · 과적합 데모",
            footer_text="3 models: Underfit [4] · Good Fit [32,16]+Dropout · Overfit [256,128,64,32]",
            parent=parent,
        )

    def _build_custom_controls(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._add_section_label(layout, "🎯  Models")
        self._stage_lbl = QLabel("—")
        self._stage_lbl.setStyleSheet(f"color: {COLORS['highlight']}; font-size: 11px; background: transparent;")
        layout.addWidget(self._stage_lbl)
        return w

    def _build_main_chart(self) -> QWidget:
        self._main_canvas = MatplotlibCanvas(nrows=1, ncols=1)
        return self._main_canvas

    def _build_custom_info(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._add_section_label(layout, "🔬  Loss Gap")
        self._gap_labels: dict[str, QLabel] = {}
        for name in _STAGE_ORDER:
            self._add_field_label(layout, name)
            v = QLabel("—")
            v.setStyleSheet(f"color: {_STAGE_COLORS[name]}; font-weight: bold; font-size: 11px; background: transparent;")
            layout.addWidget(v)
            self._gap_labels[name] = v
        return w

    def _get_model_and_data(self) -> tuple:
        # Used only for the first stage; subsequent stages handled in _on_train_complete
        name = _STAGE_ORDER[0]
        model = make_model(name, float(self._inp_learning_rate.text()))
        return model, self._x_tr, self._y_tr

    def _on_train_clicked(self):
        """Override to reset and start 3-stage sequential training."""
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()
        self._trained = {}
        self._stage_idx = 0
        self._loss_history = {"loss": [], "val_loss": []}
        self._epoch_bar.setValue(0)
        self._btn_train.setEnabled(False)
        self._btn_stop.setEnabled(True)
        self._start_stage(0)

    def _start_stage(self, idx: int):
        name = _STAGE_ORDER[idx]
        self._stage_lbl.setText(f"Training: {name}…")
        self._current_stage_name = name
        self._total_epochs = int(self._inp_epochs.text())
        model = make_model(name, float(self._inp_learning_rate.text()))
        self._current_model = model
        self._worker = TrainWorker(model, self._x_tr, self._y_tr,
                                   self._total_epochs, val_split=0.1)
        self._worker.epoch_done.connect(self._on_epoch_done)
        self._worker.train_done.connect(self._on_stage_done)
        self._worker.train_error.connect(
            lambda e: self._epoch_label.setText(f"Error: {e}")
        )
        self._worker.start()

    def _on_stage_done(self, history):
        name = self._current_stage_name
        x_in = self._x_plot.reshape(-1, 1).astype(np.float32)
        self._trained[name] = self._current_model.predict(x_in, verbose=0).flatten()

        # Compute loss gap
        logs = history.history
        tl = logs["loss"][-1]
        vl = logs.get("val_loss", [tl])[-1]
        self._gap_labels[name].setText(f"T:{tl:.4f} V:{vl:.4f}")

        self._stage_idx += 1
        if self._stage_idx < len(_STAGE_ORDER):
            self._loss_history = {"loss": [], "val_loss": []}
            self._start_stage(self._stage_idx)
        else:
            self._on_all_stages_done()

    def _on_all_stages_done(self):
        self._epoch_label.setText("Done ✓")
        self._btn_train.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._stage_lbl.setText("All 3 models trained")
        self._draw_comparison()

    def _draw_comparison(self):
        ax = self._main_canvas.ax
        ax.cla()
        ax.set_facecolor(COLORS["bg"])
        ax.scatter(self._x_tr.flatten(), self._y_tr.flatten(),
                   color=COLORS["text_muted"], s=6, alpha=0.4, label="Data")
        ax.plot(self._x_plot, self._y_true,
                color=COLORS["text_dim"], linewidth=1.5, linestyle=":", label="True fn", alpha=0.6)
        for name, y_pred in self._trained.items():
            ax.plot(self._x_plot, y_pred,
                    color=_STAGE_COLORS[name], linewidth=1.5, label=name)
        ax.legend(facecolor=COLORS["card"], edgecolor=COLORS["border"],
                  labelcolor=COLORS["text_dim"], fontsize=9)
        ax.set_title("Overfitting Comparison", color=COLORS["text_dim"], fontsize=10)
        for sp in ax.spines.values():
            sp.set_edgecolor(COLORS["border"])
        ax.tick_params(colors=COLORS["text_muted"])
        ax.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.5)
        self._main_canvas.draw()

    def _reset_custom(self):
        self._trained = {}
        self._stage_idx = 0
        self._stage_lbl.setText("—")
        for v in self._gap_labels.values():
            v.setText("—")
        self._main_canvas.clear()
        self._main_canvas.draw()

    # Disable the base reset of layers/activation since Lab3 uses presets
    def _on_reset_clicked(self):
        self._on_stop_clicked()
        self._inp_epochs.setText(str(self.DEFAULT_PARAMS["epochs"]))
        self._inp_learning_rate.setText(str(self.DEFAULT_PARAMS["lr"]))
        for lbl in self._stat_labels.values():
            lbl.setText("—")
        self._epoch_bar.setValue(0)
        self._epoch_label.setText("Ready")
        self._loss_history = {"loss": [], "val_loss": []}
        self.loss_canvas.clear()
        self.loss_canvas.draw()
        self._reset_custom()
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
.venv/Scripts/python.exe -m pytest week4/neural_network_visualizer_pyside6/tests/test_models.py -v
```
Expected: 9 PASSED

- [ ] **Step 6: Commit**

```bash
git add week4/neural_network_visualizer_pyside6/labs/lab3_overfitting/
git commit -m "feat: Lab3 — overfitting demo with 3-stage sequential training"
```

---

## Task 9: Lab 4 — 진자 예측

**Files:**
- Create: `week4/neural_network_visualizer_pyside6/labs/lab4_pendulum/lab_meta.py`
- Create: `week4/neural_network_visualizer_pyside6/labs/lab4_pendulum/model.py`
- Create: `week4/neural_network_visualizer_pyside6/labs/lab4_pendulum/window.py`

- [ ] **Step 1: 모델 테스트 추가** (`tests/test_models.py` 하단)

```python
def test_lab4_make_data_shape():
    from labs.lab4_pendulum.model import make_data
    X, Y = make_data()
    assert X.shape == (2000, 2)   # (L, theta0)
    assert Y.shape == (2000, 1)   # period T

def test_lab4_rk4_simulation():
    from labs.lab4_pendulum.model import rk4_simulate
    t, theta = rk4_simulate(L=1.0, theta0_deg=30.0)
    assert len(t) > 10
    assert abs(float(theta[0]) - np.radians(30.0)) < 0.01

def test_lab4_theoretical_period():
    from labs.lab4_pendulum.model import theoretical_period
    import numpy as np
    T = theoretical_period(L=1.0, theta0_deg=5.0)
    assert abs(T - 2 * np.pi * np.sqrt(1.0 / 9.8)) < 0.01
```

- [ ] **Step 2: lab_meta.py 작성**

```python
# labs/lab4_pendulum/lab_meta.py
LAB_META = {
    "id": "lab4_pendulum",
    "title": "Lab 4 · 진자 예측",
    "icon": "🕰️",
    "description": "Pendulum Period — RK4 Simulation",
    "window_class": "labs.lab4_pendulum.window.Lab4Window",
}
```

- [ ] **Step 3: model.py 작성**

```python
# labs/lab4_pendulum/model.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import numpy as np
import tensorflow as tf
from tensorflow import keras

G = 9.8
N_SAMPLES = 2000


def theoretical_period(L: float, theta0_deg: float) -> float:
    theta0 = np.radians(theta0_deg)
    T0 = 2 * np.pi * np.sqrt(L / G)
    correction = (1 + (1 / 16) * theta0 ** 2 + (11 / 3072) * theta0 ** 4)
    return float(T0 * correction)


def rk4_simulate(L: float, theta0_deg: float,
                 dt: float = 0.02, t_max: float = 10.0):
    theta0 = np.radians(theta0_deg)
    t = np.arange(0, t_max, dt)
    theta = np.zeros(len(t))
    omega = np.zeros(len(t))
    theta[0] = theta0

    def d_omega(th):
        return -(G / L) * np.sin(th)

    for i in range(len(t) - 1):
        k1 = omega[i]
        l1 = d_omega(theta[i])
        k2 = omega[i] + 0.5 * dt * l1
        l2 = d_omega(theta[i] + 0.5 * dt * k1)
        k3 = omega[i] + 0.5 * dt * l2
        l3 = d_omega(theta[i] + 0.5 * dt * k2)
        k4 = omega[i] + dt * l3
        l4 = d_omega(theta[i] + dt * k3)
        theta[i + 1] = theta[i] + (dt / 6) * (k1 + 2*k2 + 2*k3 + k4)
        omega[i + 1] = omega[i] + (dt / 6) * (l1 + 2*l2 + 2*l3 + l4)

    return t, theta


def make_data():
    rng = np.random.default_rng(7)
    L = rng.uniform(0.2, 3.0, N_SAMPLES)
    theta0 = rng.uniform(5, 75, N_SAMPLES)
    T = np.array([theoretical_period(l, t) for l, t in zip(L, theta0)])
    X = np.stack([L, theta0], axis=1).astype(np.float32)
    Y = T.reshape(-1, 1).astype(np.float32)
    return X, Y


def make_model(layers: list[int], activation: str, lr: float) -> keras.Model:
    model = keras.Sequential()
    model.add(keras.layers.Input(shape=(2,)))
    for units in layers:
        model.add(keras.layers.Dense(units, activation=activation))
        model.add(keras.layers.Dropout(0.1))
    model.add(keras.layers.Dense(1, activation="linear"))
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss="mse",
        metrics=["mae"],
    )
    return model
```

- [ ] **Step 4: window.py 작성**

```python
# labs/lab4_pendulum/window.py
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt
from shared.base_lab_window import BaseLabWindow
from shared.matplotlib_canvas import MatplotlibCanvas
from shared.colors import COLORS
from .model import make_data, make_model, theoretical_period, rk4_simulate


class Lab4Window(BaseLabWindow):
    DEFAULT_PARAMS = {
        "layers": "[64, 32, 16]",
        "activation": "relu",
        "epochs": 500,
        "lr": 0.001,
    }

    def __init__(self, parent=None):
        self._x_train, self._y_train = make_data()
        super().__init__(
            title="Lab 4 · 진자 예측",
            footer_text="Input: (L, θ₀) → T · RK4 Simulation · 500 epochs",
            parent=parent,
        )

    def _build_custom_controls(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._add_section_label(layout, "🎯  Pendulum Test")

        self._L_lbl = QLabel("Length L (m): 1.0")
        self._L_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px; background: transparent;")
        layout.addWidget(self._L_lbl)
        self._L_slider = QSlider(Qt.Orientation.Horizontal)
        self._L_slider.setRange(2, 30)   # 0.2 ~ 3.0 m (×10)
        self._L_slider.setValue(10)
        self._L_slider.valueChanged.connect(self._on_L_changed)
        layout.addWidget(self._L_slider)

        self._th_lbl = QLabel("Initial θ₀ (°): 30")
        self._th_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px; background: transparent;")
        layout.addWidget(self._th_lbl)
        self._th_slider = QSlider(Qt.Orientation.Horizontal)
        self._th_slider.setRange(5, 75)
        self._th_slider.setValue(30)
        self._th_slider.valueChanged.connect(self._on_theta_changed)
        layout.addWidget(self._th_slider)
        return w

    def _build_main_chart(self) -> QWidget:
        self._main_canvas = MatplotlibCanvas(nrows=1, ncols=2)
        return self._main_canvas

    def _build_custom_info(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._add_section_label(layout, "🔬  Period")
        self._period_labels: dict[str, QLabel] = {}
        for key in ["Theory (s)", "Predicted (s)", "MAPE (%)"]:
            self._add_field_label(layout, key)
            v = QLabel("—")
            v.setStyleSheet(f"color: {COLORS['highlight']}; font-weight: bold; font-size: 12px; background: transparent;")
            layout.addWidget(v)
            self._period_labels[key] = v
        return w

    def _get_model_and_data(self) -> tuple:
        model = make_model(self._parse_layers(),
                           self._inp_activation.currentText(),
                           float(self._inp_learning_rate.text()))
        return model, self._x_train, self._y_train

    def _on_train_complete(self, history):
        super()._on_train_complete(history)
        self._update_charts()

    def _on_L_changed(self, v: int):
        self._L_lbl.setText(f"Length L (m): {v / 10:.1f}")
        self._update_charts()

    def _on_theta_changed(self, v: int):
        self._th_lbl.setText(f"Initial θ₀ (°): {v}")
        self._update_charts()

    def _update_charts(self):
        if self._current_model is None:
            return
        L = self._L_slider.value() / 10.0
        theta0 = float(self._th_slider.value())

        # Period prediction over angle range
        angles = np.linspace(5, 75, 60)
        Ls = np.full(60, L)
        X_in = np.stack([Ls, angles], axis=1).astype(np.float32)
        T_pred = self._current_model.predict(X_in, verbose=0).flatten()
        T_theory = np.array([theoretical_period(L, a) for a in angles])

        # Single point
        T_pred_pt = float(self._current_model.predict(
            np.array([[L, theta0]], dtype=np.float32), verbose=0
        ))
        T_theory_pt = theoretical_period(L, theta0)
        mape = abs(T_theory_pt - T_pred_pt) / T_theory_pt * 100
        self._period_labels["Theory (s)"].setText(f"{T_theory_pt:.4f}")
        self._period_labels["Predicted (s)"].setText(f"{T_pred_pt:.4f}")
        self._period_labels["MAPE (%)"].setText(f"{mape:.2f}")

        # RK4 simulation
        t_sim, theta_sim = rk4_simulate(L, theta0)

        axes = self._main_canvas.axes   # shape (2,)
        ax1, ax2 = axes[0], axes[1]

        ax1.cla()
        ax1.set_facecolor(COLORS["bg"])
        ax1.plot(angles, T_theory, color=COLORS["accent"], linewidth=2, label="Theory")
        ax1.plot(angles, T_pred, color=COLORS["danger"], linewidth=1.5,
                 linestyle="--", label="Predicted")
        ax1.axvline(theta0, color=COLORS["highlight"], linewidth=0.8, alpha=0.6)
        ax1.set_xlabel("θ₀ (°)", color=COLORS["text_dim"])
        ax1.set_ylabel("T (s)", color=COLORS["text_dim"])
        ax1.set_title(f"Period vs Angle  L={L:.1f}m", color=COLORS["text_dim"], fontsize=9)
        ax1.legend(facecolor=COLORS["card"], edgecolor=COLORS["border"],
                   labelcolor=COLORS["text_dim"], fontsize=8)
        for sp in ax1.spines.values():
            sp.set_edgecolor(COLORS["border"])
        ax1.tick_params(colors=COLORS["text_muted"])
        ax1.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.5)

        ax2.cla()
        ax2.set_facecolor(COLORS["bg"])
        ax2.plot(t_sim[:500], np.degrees(theta_sim[:500]),
                 color=COLORS["success"], linewidth=1.2)
        ax2.set_xlabel("t (s)", color=COLORS["text_dim"])
        ax2.set_ylabel("θ (°)", color=COLORS["text_dim"])
        ax2.set_title(f"RK4 Simulation  θ₀={theta0:.0f}°", color=COLORS["text_dim"], fontsize=9)
        for sp in ax2.spines.values():
            sp.set_edgecolor(COLORS["border"])
        ax2.tick_params(colors=COLORS["text_muted"])
        ax2.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.5)

        self._main_canvas.fig.tight_layout(pad=1.5)
        self._main_canvas.draw()

    def _reset_custom(self):
        self._L_slider.setValue(10)
        self._th_slider.setValue(30)
        for v in self._period_labels.values():
            v.setText("—")
        self._main_canvas.clear()
        self._main_canvas.draw()
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
.venv/Scripts/python.exe -m pytest week4/neural_network_visualizer_pyside6/tests/test_models.py -v
```
Expected: 12 PASSED

- [ ] **Step 6: Commit**

```bash
git add week4/neural_network_visualizer_pyside6/labs/lab4_pendulum/
git commit -m "feat: Lab4 — pendulum period prediction + RK4 simulation"
```

---

## Task 10: 플러그인 발견 테스트 통과 + 통합 검증

**Files:**
- Test: `week4/neural_network_visualizer_pyside6/tests/test_plugin_discovery.py`

- [ ] **Step 1: 플러그인 발견 테스트 재실행**

```bash
.venv/Scripts/python.exe -m pytest week4/neural_network_visualizer_pyside6/tests/test_plugin_discovery.py -v
```
Expected: 2 PASSED (4개 lab_meta.py 모두 발견됨)

- [ ] **Step 2: 전체 테스트 스위트 실행**

```bash
.venv/Scripts/python.exe -m pytest week4/neural_network_visualizer_pyside6/tests/ -v
```
Expected: 모든 테스트 PASSED (16개 이상)

- [ ] **Step 3: 런처 스모크 실행** (UI 확인)

```bash
.venv/Scripts/python.exe week4/neural_network_visualizer_pyside6/main.py
```
확인 항목:
- 런처 창에 4개 Lab 카드 표시
- 각 카드 "열기" 클릭 시 Lab 서브윈도우 오픈
- 헤더 우측 고양이 SVG 표시
- 앱 시작 300ms 후 자동 학습 시작
- Train/Stop/Reset 버튼 동작 확인
- 학습 완료 후 메인 차트 업데이트 확인

- [ ] **Step 4: 최종 Commit**

```bash
git add week4/neural_network_visualizer_pyside6/
git commit -m "feat: week4 NN visualizer complete — 4 labs, dark theme, plugin discovery"
```

---

## Self-Review

**Spec 커버리지 점검:**
- ✅ 런처 + 플러그인 발견 (Task 5)
- ✅ Lab 1 함수 근사 · MSE · R² (Task 6)
- ✅ Lab 2 포물선 · 슬라이더 · 오차 (Task 7)
- ✅ Lab 3 과적합 3모델 순차 학습 (Task 8)
- ✅ Lab 4 진자 + RK4 + MAPE (Task 9)
- ✅ QThread + stop_flag (Task 3)
- ✅ 하이브리드 학습 (자동 시작 + 재학습) (Task 4: `QTimer.singleShot`)
- ✅ Dark Tokyo Night 테마 (Task 1)
- ✅ 고양이 SVG 헤더 (Task 4)
- ✅ Matplotlib dark embed (Task 2)

**타입 일관성:**
- `_inp_hidden_layers`, `_inp_epochs`, `_inp_learning_rate`, `_inp_activation` — Task 4 정의, Task 6~9 사용 ✓
- `_current_model` — Task 4 `_on_train_clicked`에서 설정, Task 6~9 `_on_train_complete`에서 사용 ✓
- `_parse_layers()` → `list[int]` — Task 4 정의, Task 6~9 사용 ✓
- `TrainWorker(model, x, y, epochs, val_split)` — Task 3 정의, Task 4/8 사용 ✓
- `MatplotlibCanvas.axes` shape `(2,)` for ncols=2 — Task 2 정의, Task 9 `axes[0], axes[1]`로 사용 ✓
