"""explorer_widget.py — 함수 탐색 탭"""
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QRadioButton, QSlider, QLabel, QCheckBox, QButtonGroup, QSizePolicy,
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from activation_model import FUNC_MAP, COLORS, leaky_relu, leaky_relu_deriv
from styles import GROUP_STYLE, SLIDER_STYLE, RADIO_STYLE


_X = np.linspace(-6, 6, 400)


class ExplorerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._func_name = "Sigmoid"
        self._alpha = 0.01
        self._show_tangent = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # ── 좌 패널 ──────────────────────────────────
        left = QWidget()
        left.setFixedWidth(280)
        left.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        vl = QVBoxLayout(left)
        vl.setSpacing(8)

        # 함수 선택
        grp_func = QGroupBox("함수 선택")
        grp_func.setStyleSheet(GROUP_STYLE)
        vf = QVBoxLayout(grp_func)
        self._btn_group = QButtonGroup(self)
        for name in FUNC_MAP:
            rb = QRadioButton(name)
            rb.setStyleSheet(RADIO_STYLE)
            if name == "Sigmoid":
                rb.setChecked(True)
            vf.addWidget(rb)
            self._btn_group.addButton(rb)
        self._btn_group.buttonClicked.connect(self._on_func_changed)
        vl.addWidget(grp_func)

        # x 슬라이더
        grp_x = QGroupBox("x 값")
        grp_x.setStyleSheet(GROUP_STYLE)
        vx = QVBoxLayout(grp_x)
        self._x_slider = QSlider(Qt.Horizontal)
        self._x_slider.setRange(-600, 600)
        self._x_slider.setValue(0)
        self._x_slider.setStyleSheet(SLIDER_STYLE)
        self._x_label = QLabel("x = 0.00")
        self._x_label.setAlignment(Qt.AlignCenter)
        vx.addWidget(self._x_slider)
        vx.addWidget(self._x_label)
        self._x_slider.valueChanged.connect(self._update)
        vl.addWidget(grp_x)

        # Leaky ReLU alpha
        grp_a = QGroupBox("Leaky α (Leaky ReLU 전용)")
        grp_a.setStyleSheet(GROUP_STYLE)
        va = QVBoxLayout(grp_a)
        self._alpha_slider = QSlider(Qt.Horizontal)
        self._alpha_slider.setRange(1, 50)
        self._alpha_slider.setValue(1)
        self._alpha_slider.setStyleSheet(SLIDER_STYLE)
        self._alpha_label = QLabel("α = 0.01")
        self._alpha_label.setAlignment(Qt.AlignCenter)
        va.addWidget(self._alpha_slider)
        va.addWidget(self._alpha_label)
        self._alpha_slider.valueChanged.connect(self._on_alpha_changed)
        self._grp_alpha = grp_a
        grp_a.setEnabled(False)
        vl.addWidget(grp_a)

        # 접선 체크박스
        self._tangent_cb = QCheckBox("접선 표시 (기울기)")
        self._tangent_cb.setStyleSheet("QCheckBox { font-size: 13px; color: #2c3e50; }")
        self._tangent_cb.stateChanged.connect(self._on_tangent_changed)
        vl.addWidget(self._tangent_cb)

        # 현재 값 표시
        grp_val = QGroupBox("현재 값")
        grp_val.setStyleSheet(GROUP_STYLE)
        vval = QVBoxLayout(grp_val)
        self._lbl_fx = QLabel("f(x) = —")
        self._lbl_dx = QLabel("f'(x) = —")
        for lbl in (self._lbl_fx, self._lbl_dx):
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #2c3e50; padding: 6px;")
        vval.addWidget(self._lbl_fx)
        vval.addWidget(self._lbl_dx)
        vl.addWidget(grp_val)

        vl.addStretch()
        layout.addWidget(left)

        # ── 우 캔버스 ─────────────────────────────────
        self._fig = Figure(figsize=(6, 4), tight_layout=True)
        self._ax = self._fig.add_subplot(111)
        self._canvas = FigureCanvas(self._fig)
        layout.addWidget(self._canvas, 1)

        self._update()

    # ── 슬롯 ──────────────────────────────────────────
    def _on_func_changed(self, btn):
        self._func_name = btn.text()
        self._grp_alpha.setEnabled(self._func_name == "Leaky ReLU")
        self._update()

    def _on_alpha_changed(self, val):
        self._alpha = val / 100.0
        self._alpha_label.setText(f"α = {self._alpha:.2f}")
        self._update()

    def _on_tangent_changed(self, state):
        self._show_tangent = bool(state)
        self._update()

    def _update(self):
        x0 = self._x_slider.value() / 100.0
        self._x_label.setText(f"x = {x0:.2f}")

        name = self._func_name
        color = COLORS[name]

        if name == "Leaky ReLU":
            f  = lambda x: leaky_relu(x, self._alpha)
            fd = lambda x: leaky_relu_deriv(x, self._alpha)
        else:
            f, fd = FUNC_MAP[name]

        y  = f(_X)
        dy = fd(_X)
        fx0  = float(f(np.array([x0]))[0]) if hasattr(f(np.array([x0])), '__len__') else float(f(x0))
        fdx0 = float(fd(np.array([x0]))[0]) if hasattr(fd(np.array([x0])), '__len__') else float(fd(x0))

        self._lbl_fx.setText(f"f({x0:.2f}) = {fx0:.4f}")
        self._lbl_dx.setText(f"f'({x0:.2f}) = {fdx0:.4f}")

        ax = self._ax
        ax.clear()
        ax.plot(_X, y,  color=color, linewidth=2.5, label=f"{name}")
        ax.plot(_X, dy, color=color, linewidth=1.5, linestyle="--", alpha=0.7, label=f"{name}' (미분)")
        ax.axhline(0, color="black", linewidth=0.8, alpha=0.4)
        ax.axvline(0, color="black", linewidth=0.8, alpha=0.4)
        ax.axvline(x0, color="#7f8c8d", linewidth=1, linestyle=":")

        ax.scatter([x0], [fx0],  color=color, s=80, zorder=5)
        ax.scatter([x0], [fdx0], color=color, s=60, zorder=5, marker="D", alpha=0.8)

        if self._show_tangent and abs(fdx0) < 50:
            margin = 1.5
            tx = np.array([x0 - margin, x0 + margin])
            ty = fdx0 * (tx - x0) + fx0
            ax.plot(tx, ty, color="#e74c3c", linewidth=1.5, linestyle="-.", alpha=0.8, label=f"접선 (기울기={fdx0:.3f})")

        ax.set_xlim(-6, 6)
        ax.set_ylim(-2.2, 2.2)
        ax.set_xlabel("x", fontsize=11)
        ax.set_ylabel("f(x)  /  f'(x)", fontsize=11)
        ax.set_title(f"{name} 함수 및 미분", fontsize=13, fontweight="bold")
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        self._canvas.draw_idle()
