"""comparison_widget.py — 비교 탭"""
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QCheckBox, QRadioButton, QSlider, QLabel, QButtonGroup, QSizePolicy,
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from activation_model import FUNC_MAP, COLORS, leaky_relu, leaky_relu_deriv
from styles import GROUP_STYLE, SLIDER_STYLE, RADIO_STYLE


class ComparisonWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._show_deriv = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # ── 좌 패널 ──────────────────────────────────
        left = QWidget()
        left.setFixedWidth(220)
        vl = QVBoxLayout(left)
        vl.setSpacing(8)

        # 함수 체크박스
        grp_fn = QGroupBox("함수 선택")
        grp_fn.setStyleSheet(GROUP_STYLE)
        vf = QVBoxLayout(grp_fn)
        self._checks: dict[str, QCheckBox] = {}
        for name, color in COLORS.items():
            cb = QCheckBox(name)
            cb.setChecked(True)
            cb.setStyleSheet(
                f"QCheckBox {{ font-size: 13px; color: {color}; font-weight: bold; }}"
            )
            cb.stateChanged.connect(self._update)
            vf.addWidget(cb)
            self._checks[name] = cb
        vl.addWidget(grp_fn)

        # 표시 모드
        grp_mode = QGroupBox("표시 모드")
        grp_mode.setStyleSheet(GROUP_STYLE)
        vm = QVBoxLayout(grp_mode)
        self._mode_grp = QButtonGroup(self)
        rb_fn = QRadioButton("함수값 f(x)")
        rb_fd = QRadioButton("미분값 f'(x)")
        rb_fn.setChecked(True)
        for rb in (rb_fn, rb_fd):
            rb.setStyleSheet(RADIO_STYLE)
            vm.addWidget(rb)
            self._mode_grp.addButton(rb)
        self._mode_grp.buttonClicked.connect(self._on_mode)
        self._rb_fn = rb_fn
        vl.addWidget(grp_mode)

        # X 범위
        grp_range = QGroupBox("X 범위")
        grp_range.setStyleSheet(GROUP_STYLE)
        vr = QVBoxLayout(grp_range)
        self._range_slider = QSlider(Qt.Horizontal)
        self._range_slider.setRange(1, 10)
        self._range_slider.setValue(6)
        self._range_slider.setStyleSheet(SLIDER_STYLE)
        self._range_label = QLabel("±6")
        self._range_label.setAlignment(Qt.AlignCenter)
        vr.addWidget(self._range_slider)
        vr.addWidget(self._range_label)
        self._range_slider.valueChanged.connect(self._on_range)
        vl.addWidget(grp_range)

        vl.addStretch()
        layout.addWidget(left)

        # ── 우 캔버스 ─────────────────────────────────
        self._fig = Figure(figsize=(6, 4), tight_layout=True)
        self._ax = self._fig.add_subplot(111)
        self._canvas = FigureCanvas(self._fig)
        layout.addWidget(self._canvas, 1)

        self._update()

    def _on_mode(self, btn):
        self._show_deriv = (btn is not self._rb_fn)
        self._update()

    def _on_range(self, val):
        self._range_label.setText(f"±{val}")
        self._update()

    def _update(self):
        xmax = self._range_slider.value()
        x = np.linspace(-xmax, xmax, 500)

        ax = self._ax
        ax.clear()

        for name, cb in self._checks.items():
            if not cb.isChecked():
                continue
            color = COLORS[name]
            if name == "Leaky ReLU":
                f, fd = leaky_relu, leaky_relu_deriv
            else:
                f, fd = FUNC_MAP[name]
            y = fd(x) if self._show_deriv else f(x)
            ax.plot(x, y, color=color, linewidth=2.2, label=name)

        ax.axhline(0, color="black", linewidth=0.8, alpha=0.4)
        ax.axvline(0, color="black", linewidth=0.8, alpha=0.4)
        ax.set_xlim(-xmax, xmax)
        ax.set_xlabel("x", fontsize=11)
        mode_str = "미분값 f'(x)" if self._show_deriv else "함수값 f(x)"
        ax.set_ylabel(mode_str, fontsize=11)
        ax.set_title(f"활성화 함수 비교 — {mode_str}", fontsize=13, fontweight="bold")
        if ax.lines:
            ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        self._canvas.draw_idle()
