"""approximation_widget.py — 함수 근사 탭"""
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLabel,
    QSlider, QRadioButton, QButtonGroup, QPushButton, QSpinBox, QDoubleSpinBox,
)
from PySide6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from approximator_model import UniversalApproximator, TARGET_FUNCTIONS, X_TRAIN, X_TEST
from styles import GROUP_STYLE, SLIDER_STYLE, RADIO_STYLE, PRIMARY_BTN, SECONDARY_BTN

_SPEED = {0: 200, 1: 100, 2: 50, 3: 20, 4: 5}
_STEPS = {0: 10,  1: 20,  2: 50, 3: 100, 4: 200}


class ApproximationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = UniversalApproximator(n_hidden=10, lr=0.01)
        self._func_name = "Sine Wave"
        self._running = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._step)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        left = QWidget(); left.setFixedWidth(280)
        vl = QVBoxLayout(left); vl.setSpacing(6)

        grp_fn = QGroupBox("목표 함수"); grp_fn.setStyleSheet(GROUP_STYLE)
        vf = QVBoxLayout(grp_fn)
        self._fn_grp = QButtonGroup(self)
        for name in TARGET_FUNCTIONS:
            rb = QRadioButton(name); rb.setStyleSheet(RADIO_STYLE)
            if name == "Sine Wave": rb.setChecked(True)
            vf.addWidget(rb); self._fn_grp.addButton(rb)
        self._fn_grp.buttonClicked.connect(self._on_func)
        vl.addWidget(grp_fn)

        grp_net = QGroupBox("네트워크 설정"); grp_net.setStyleSheet(GROUP_STYLE)
        vn = QVBoxLayout(grp_net)
        vn.addWidget(QLabel("뉴런 수:"))
        self._neuron_sl = QSlider(Qt.Horizontal); self._neuron_sl.setRange(2, 100)
        self._neuron_sl.setValue(10); self._neuron_sl.setStyleSheet(SLIDER_STYLE)
        self._neuron_lbl = QLabel("10"); self._neuron_lbl.setAlignment(Qt.AlignCenter)
        self._neuron_sl.valueChanged.connect(lambda v: self._neuron_lbl.setText(str(v)))
        vn.addWidget(self._neuron_sl); vn.addWidget(self._neuron_lbl)
        vn.addWidget(QLabel("학습률:"))
        self._lr_spin = QDoubleSpinBox(); self._lr_spin.setRange(0.001, 0.1)
        self._lr_spin.setSingleStep(0.001); self._lr_spin.setDecimals(3); self._lr_spin.setValue(0.01)
        vn.addWidget(self._lr_spin)
        vl.addWidget(grp_net)

        grp_tr = QGroupBox("학습 설정"); grp_tr.setStyleSheet(GROUP_STYLE)
        vt = QVBoxLayout(grp_tr)
        vt.addWidget(QLabel("에포크:"))
        self._ep_spin = QSpinBox(); self._ep_spin.setRange(500, 20000)
        self._ep_spin.setSingleStep(500); self._ep_spin.setValue(5000)
        vt.addWidget(self._ep_spin)
        vt.addWidget(QLabel("속도:"))
        self._speed_sl = QSlider(Qt.Horizontal); self._speed_sl.setRange(0, 4)
        self._speed_sl.setValue(3); self._speed_sl.setStyleSheet(SLIDER_STYLE)
        vt.addWidget(self._speed_sl)
        vl.addWidget(grp_tr)

        self._btn_start = QPushButton("▶ 학습 시작"); self._btn_start.setStyleSheet(PRIMARY_BTN)
        self._btn_reset = QPushButton("↺ 초기화"); self._btn_reset.setStyleSheet(SECONDARY_BTN)
        self._btn_start.clicked.connect(self._start)
        self._btn_reset.clicked.connect(self._reset)
        vl.addWidget(self._btn_start); vl.addWidget(self._btn_reset)

        self._mse_lbl = QLabel("MSE: —")
        self._mse_lbl.setAlignment(Qt.AlignCenter)
        self._mse_lbl.setStyleSheet("font-size:18px;font-weight:bold;color:#e74c3c;padding:8px")
        vl.addWidget(self._mse_lbl); vl.addStretch()
        layout.addWidget(left)

        self._fig = Figure(figsize=(7, 4.5), tight_layout=True)
        self._ax_fn  = self._fig.add_subplot(2, 1, 1)
        self._ax_loss = self._fig.add_subplot(2, 1, 2)
        self._canvas = FigureCanvas(self._fig)
        layout.addWidget(self._canvas, 1)
        self._draw()

    def _on_func(self, btn):
        self._func_name = btn.text(); self._reset()

    def _start(self):
        self._model.reset(self._neuron_sl.value(), self._lr_spin.value())
        self._running = True
        self._timer.setInterval(_SPEED[self._speed_sl.value()])
        self._timer.start()
        self._btn_start.setEnabled(False)

    def _reset(self):
        self._timer.stop(); self._running = False
        self._model.reset(self._neuron_sl.value(), self._lr_spin.value())
        self._btn_start.setEnabled(True)
        self._mse_lbl.setText("MSE: —"); self._draw()

    def _step(self):
        fn = TARGET_FUNCTIONS[self._func_name]
        y_train = fn(X_TRAIN)
        steps = _STEPS[self._speed_sl.value()]
        for _ in range(steps):
            if self._model.step >= self._ep_spin.value(): break
            self._model.train_step(X_TRAIN, y_train)
        mse = float(np.mean((self._model.forward(X_TEST) - fn(X_TEST))**2))
        self._mse_lbl.setText(f"MSE: {mse:.6f}  (Step {self._model.step})")
        self._draw()
        if self._model.step >= self._ep_spin.value():
            self._timer.stop(); self._btn_start.setEnabled(True)

    def _draw(self):
        fn = TARGET_FUNCTIONS[self._func_name]
        y_true = fn(X_TEST)
        y_pred = self._model.forward(X_TEST)

        ax = self._ax_fn; ax.clear()
        ax.plot(X_TEST, y_true, "b-", lw=2, label="실제 함수", alpha=0.8)
        ax.plot(X_TEST, y_pred, "r--", lw=2, label=f"NN ({self._model.n_hidden}개 뉴런)")
        ax.scatter(X_TRAIN[::10], fn(X_TRAIN)[::10], c="green", s=20, alpha=0.5, label="학습 데이터")
        ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
        ax.set_title(f"{self._func_name} 근사", fontsize=11, fontweight="bold")

        ax = self._ax_loss; ax.clear()
        if self._model.loss_history:
            ax.plot(self._model.loss_history, lw=1.5, color="#2980b9")
            ax.set_yscale("log")
        ax.set_title("Loss (log scale)", fontsize=10); ax.grid(True, alpha=0.3)
        self._canvas.draw_idle()
