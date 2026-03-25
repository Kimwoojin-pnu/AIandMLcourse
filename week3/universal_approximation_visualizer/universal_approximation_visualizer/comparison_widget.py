"""comparison_widget.py — 뉴런 수 비교 탭"""
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup, QPushButton, QLabel,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from approximator_model import UniversalApproximator, TARGET_FUNCTIONS, X_TRAIN, X_TEST
from styles import RADIO_STYLE, PRIMARY_BTN

_NEURON_COUNTS = [3, 10, 50]


class ComparisonWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._func_name = "Sine Wave"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # 상단 컨트롤
        top = QHBoxLayout()
        self._fn_grp = QButtonGroup(self)
        for name in TARGET_FUNCTIONS:
            rb = QRadioButton(name); rb.setStyleSheet(RADIO_STYLE)
            if name == "Sine Wave": rb.setChecked(True)
            top.addWidget(rb); self._fn_grp.addButton(rb)
        self._fn_grp.buttonClicked.connect(self._on_func)
        top.addStretch()
        btn = QPushButton("▶ 모두 학습 (5000 에포크)")
        btn.setStyleSheet(PRIMARY_BTN); btn.setFixedWidth(220)
        btn.clicked.connect(self._train_all)
        top.addWidget(btn)
        layout.addLayout(top)

        self._status = QLabel("버튼을 클릭하면 3/10/50 뉴런 모델을 각각 학습합니다.")
        self._status.setStyleSheet("font-size:12px;color:#636e72;padding:4px")
        layout.addWidget(self._status)

        self._fig = Figure(figsize=(10, 4), tight_layout=True)
        self._canvas = FigureCanvas(self._fig)
        layout.addWidget(self._canvas, 1)
        self._draw_placeholder()

    def _on_func(self, btn):
        self._func_name = btn.text()
        self._draw_placeholder()

    def _train_all(self):
        self._status.setText("학습 중...")
        fn = TARGET_FUNCTIONS[self._func_name]
        y_train = fn(X_TRAIN)
        y_true  = fn(X_TEST)

        self._fig.clear()
        axes = self._fig.subplots(1, 3)
        for ax, n in zip(axes, _NEURON_COUNTS):
            m = UniversalApproximator(n_hidden=n, lr=0.01)
            m.train_epochs(X_TRAIN, y_train, 5000)
            y_pred = m.forward(X_TEST)
            mse = float(np.mean((y_pred - y_true)**2))
            ax.plot(X_TEST, y_true,  "b-",  lw=2, label="실제", alpha=0.8)
            ax.plot(X_TEST, y_pred,  "r--", lw=2, label=f"NN")
            ax.scatter(X_TRAIN[::10], fn(X_TRAIN)[::10], c="green", s=15, alpha=0.4)
            ax.set_title(f"{n}개 뉴런\nMSE={mse:.5f}", fontsize=11, fontweight="bold")
            ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
        self._canvas.draw_idle()
        self._status.setText(f"완료 — {self._func_name} / 각 5000 에포크 학습")

    def _draw_placeholder(self):
        fn = TARGET_FUNCTIONS[self._func_name]
        y_true = fn(X_TEST)
        self._fig.clear()
        axes = self._fig.subplots(1, 3)
        for ax, n in zip(axes, _NEURON_COUNTS):
            ax.plot(X_TEST, y_true, "b-", lw=2, label="실제 함수")
            ax.set_title(f"{n}개 뉴런 (미학습)", fontsize=11)
            ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
        self._canvas.draw_idle()
