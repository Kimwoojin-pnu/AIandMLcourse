"""
manual_widget.py
직접 조작 탭 — 가중치·편향 슬라이더로 결정 경계를 실시간 조작
"""
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QSlider, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as mpatches

from utils import setup_korean_font, X_DATA, GATE_LABELS
from styles import (
    GROUP_STYLE, SECONDARY_BTN, SUCCESS_BTN,
    TABLE_STYLE, SLIDER_STYLE,
)

setup_korean_font()

# 사전 설정값 (게이트 이름, w1, w2, bias)
_PRESETS = [
    ("AND 프리셋",  1.0,  1.0, -1.5),
    ("OR 프리셋",   1.0,  1.0, -0.5),
    ("초기화",      0.5,  0.5,  0.0),
]


class _ParamSlider(QWidget):
    """레이블 + 슬라이더 + 값 표시 복합 위젯"""

    def __init__(self, label: str, min_v: float, max_v: float,
                 default: float, parent=None):
        super().__init__(parent)
        self._min = min_v
        self._max = max_v
        self._callback = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(3)

        # 헤더 (라벨 + 현재값)
        header = QHBoxLayout()
        self._lbl = QLabel(label)
        self._lbl.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #34495e;"
        )
        self._val_lbl = QLabel(f"{default:+.2f}")
        self._val_lbl.setFixedWidth(52)
        self._val_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._val_lbl.setStyleSheet(
            "font-size: 13px; color: #2980b9; font-weight: bold;"
        )
        header.addWidget(self._lbl)
        header.addStretch()
        header.addWidget(self._val_lbl)
        layout.addLayout(header)

        # 슬라이더 (×100 스케일)
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(int(min_v * 100), int(max_v * 100))
        self._slider.setValue(int(default * 100))
        self._slider.setStyleSheet(SLIDER_STYLE)
        self._slider.valueChanged.connect(self._on_change)
        layout.addWidget(self._slider)

        # 범위 표시
        rl = QHBoxLayout()
        for t in [f"{min_v:.1f}", "0", f"{max_v:.1f}"]:
            l = QLabel(t)
            l.setStyleSheet("font-size: 9px; color: #95a5a6;")
            l.setAlignment(Qt.AlignCenter)
            rl.addWidget(l, 1)
        layout.addLayout(rl)

    def _on_change(self, raw: int):
        v = raw / 100.0
        self._val_lbl.setText(f"{v:+.2f}")
        if self._callback:
            self._callback()

    def value(self) -> float:
        return self._slider.value() / 100.0

    def set_value(self, v: float):
        self._slider.blockSignals(True)
        self._slider.setValue(int(v * 100))
        self._val_lbl.setText(f"{v:+.2f}")
        self._slider.blockSignals(False)

    def on_change(self, fn):
        self._callback = fn


class ManualWidget(QWidget):
    """직접 조작 탭 위젯"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._update_all()

    # ─────────────────────────────────────────
    # UI 구성
    # ─────────────────────────────────────────
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        root.addWidget(self._build_left(), 0)
        root.addWidget(self._build_right(), 1)

    def _build_left(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(330)
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # 타이틀
        title = QLabel("가중치 · 편향 직접 조작")
        title.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #1a2634;"
            "padding: 4px 2px;"
        )
        layout.addWidget(title)

        # 슬라이더 그룹
        slider_grp = QGroupBox("파라미터 조작")
        slider_grp.setStyleSheet(GROUP_STYLE)
        sg_layout = QVBoxLayout(slider_grp)

        self._w1_slider = _ParamSlider("가중치  w₁", -3.0, 3.0, 1.0)
        self._w2_slider = _ParamSlider("가중치  w₂", -3.0, 3.0, 1.0)
        self._b_slider  = _ParamSlider("편향  b",    -3.0, 3.0, -1.5)

        for s in [self._w1_slider, self._w2_slider, self._b_slider]:
            s.on_change(self._update_all)
            sg_layout.addWidget(s)

        layout.addWidget(slider_grp)

        # 현재 수식 표시
        formula_grp = QGroupBox("현재 수식")
        formula_grp.setStyleSheet(GROUP_STYLE)
        fl = QVBoxLayout(formula_grp)
        self._formula_lbl = QLabel()
        self._formula_lbl.setWordWrap(True)
        self._formula_lbl.setStyleSheet("""
            font-family: 'Courier New', monospace;
            font-size: 12px;
            background: #f0f4f8;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 10px 12px;
            color: #1a2634;
            line-height: 1.7;
        """)
        fl.addWidget(self._formula_lbl)
        layout.addWidget(formula_grp)

        # 예측 결과 테이블
        pred_grp = QGroupBox("입력별 예측 결과")
        pred_grp.setStyleSheet(GROUP_STYLE)
        pl = QVBoxLayout(pred_grp)
        self._pred_table = QTableWidget(4, 4)
        self._pred_table.setHorizontalHeaderLabels(["x₁", "x₂", "z = w·x+b", "예측 ŷ"])
        self._pred_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._pred_table.verticalHeader().setVisible(False)
        self._pred_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._pred_table.setStyleSheet(TABLE_STYLE)
        self._pred_table.setMaximumHeight(150)
        pl.addWidget(self._pred_table)
        layout.addWidget(pred_grp)

        # 진리표 비교
        truth_grp = QGroupBox("AND / OR / XOR 비교")
        truth_grp.setStyleSheet(GROUP_STYLE)
        tl = QVBoxLayout(truth_grp)
        self._truth_table = QTableWidget(4, 5)
        self._truth_table.setHorizontalHeaderLabels(["x₁", "x₂", "AND", "OR", "XOR"])
        self._truth_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._truth_table.verticalHeader().setVisible(False)
        self._truth_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._truth_table.setStyleSheet(TABLE_STYLE)
        self._truth_table.setMaximumHeight(150)
        self._fill_truth_table()
        tl.addWidget(self._truth_table)
        layout.addWidget(truth_grp)

        # 프리셋 버튼
        preset_grp = QGroupBox("빠른 프리셋")
        preset_grp.setStyleSheet(GROUP_STYLE)
        preset_layout = QHBoxLayout(preset_grp)
        for name, w1, w2, b in _PRESETS:
            btn = QPushButton(name)
            btn.setStyleSheet(SECONDARY_BTN if "초기화" not in name else SUCCESS_BTN)
            btn.clicked.connect(
                lambda _, _w1=w1, _w2=w2, _b=b: self._apply_preset(_w1, _w2, _b)
            )
            preset_layout.addWidget(btn)
        layout.addWidget(preset_grp)

        layout.addStretch()
        return panel

    def _build_right(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        self._fig = Figure(figsize=(9, 7), dpi=85, facecolor="white")
        self._canvas = FigureCanvas(self._fig)
        self._canvas.setStyleSheet("border: 1px solid #dee2e6; border-radius: 4px;")
        layout.addWidget(self._canvas)

        return panel

    # ─────────────────────────────────────────
    # 업데이트
    # ─────────────────────────────────────────
    def _update_all(self):
        self._update_formula()
        self._update_pred_table()
        self._update_plot()

    def _update_formula(self):
        w1 = self._w1_slider.value()
        w2 = self._w2_slider.value()
        b  = self._b_slider.value()

        formula = (
            f"y = step({w1:+.2f}·x₁  {'+' if w2>=0 else ''}{w2:.2f}·x₂  "
            f"{'+' if b>=0 else ''}{b:.2f})"
        )
        if abs(w2) > 0.001:
            slope = -w1 / w2
            inter = -b  / w2
            boundary = f"\n결정 경계: x₂ = {slope:+.2f}·x₁ {'+' if inter>=0 else ''}{inter:.2f}"
        elif abs(w1) > 0.001:
            boundary = f"\n결정 경계: x₁ = {-b/w1:+.2f}  (수직선)"
        else:
            boundary = "\n결정 경계: 없음 (w₁=w₂=0)"

        self._formula_lbl.setText(formula + boundary)

    def _update_pred_table(self):
        w1 = self._w1_slider.value()
        w2 = self._w2_slider.value()
        b  = self._b_slider.value()

        for row, pt in enumerate(X_DATA):
            z    = w1 * pt[0] + w2 * pt[1] + b
            pred = 1 if z >= 0 else 0
            vals = [str(int(pt[0])), str(int(pt[1])), f"{z:+.3f}", str(pred)]
            for col, txt in enumerate(vals):
                item = QTableWidgetItem(txt)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 3:
                    c = QColor("#27ae60") if pred == 1 else QColor("#2980b9")
                    item.setForeground(c)
                    item.setFont(QFont("", -1, QFont.Bold))
                self._pred_table.setItem(row, col, item)

    def _fill_truth_table(self):
        """AND/OR/XOR 고정 진리표"""
        for row, pt in enumerate(X_DATA):
            and_v = GATE_LABELS["AND"][row]
            or_v  = GATE_LABELS["OR"][row]
            xor_v = GATE_LABELS["XOR"][row]
            for col, (val, gate) in enumerate(
                [(int(pt[0]), None), (int(pt[1]), None),
                 (and_v, "AND"), (or_v, "OR"), (xor_v, "XOR")]
            ):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                if gate and val == 1:
                    item.setForeground(QColor("#e74c3c"))
                    item.setFont(QFont("", -1, QFont.Bold))
                self._truth_table.setItem(row, col, item)

    # ─────────────────────────────────────────
    # 시각화
    # ─────────────────────────────────────────
    def _update_plot(self):
        w1 = self._w1_slider.value()
        w2 = self._w2_slider.value()
        b  = self._b_slider.value()

        self._fig.clear()

        # 두 subplot: 결정 경계 + 순입력(net input) 히트맵
        ax1 = self._fig.add_subplot(1, 2, 1)
        ax2 = self._fig.add_subplot(1, 2, 2)

        xmin, xmax, ymin, ymax = -0.5, 1.5, -0.5, 1.5

        xx, yy = np.meshgrid(
            np.linspace(xmin, xmax, 300),
            np.linspace(ymin, ymax, 300),
        )
        nets = w1 * xx + w2 * yy + b
        Z    = (nets >= 0).astype(int)

        # ── Subplot 1: 결정 경계 ──────────────────────
        ax1.contourf(xx, yy, Z, alpha=0.18,
                     levels=[-0.5, 0.5, 1.5],
                     colors=["#3498db", "#e74c3c"])
        try:
            ax1.contour(xx, yy, Z, levels=[0.5],
                        colors=["#2c3e50"], linewidths=2.2, linestyles="--")
        except Exception:
            pass

        # 데이터 포인트
        for i, pt in enumerate(X_DATA):
            z_pt  = w1 * pt[0] + w2 * pt[1] + b
            pred  = 1 if z_pt >= 0 else 0
            color = "#e74c3c" if pred == 1 else "#3498db"
            marker = "o" if pred == 1 else "s"
            ax1.scatter(pt[0], pt[1], c=color, marker=marker,
                        s=240, edgecolors="black", linewidth=1.8, zorder=6)
            ax1.text(pt[0] + 0.06, pt[1] + 0.06,
                     f"({int(pt[0])},{int(pt[1])})\n→{pred}",
                     fontsize=9, color="#2c3e50")

        ax1.set_xlim(xmin, xmax)
        ax1.set_ylim(ymin, ymax)
        ax1.set_xlabel("x₁", fontsize=11)
        ax1.set_ylabel("x₂", fontsize=11)
        ax1.set_title(f"결정 경계\n"
                      f"w₁={w1:+.2f}, w₂={w2:+.2f}, b={b:+.2f}",
                      fontsize=11, fontweight="bold")
        ax1.grid(True, alpha=0.25)

        patches = [
            mpatches.Patch(facecolor="#e74c3c", alpha=0.5, label="예측 = 1"),
            mpatches.Patch(facecolor="#3498db", alpha=0.5, label="예측 = 0"),
        ]
        ax1.legend(handles=patches, loc="upper left", fontsize=9)

        # ── Subplot 2: 순입력 z 히트맵 ───────────────────
        vmax = max(abs(nets.min()), abs(nets.max()), 0.5)
        im = ax2.contourf(xx, yy, nets, levels=20,
                          cmap="RdBu_r", vmin=-vmax, vmax=vmax)
        self._fig.colorbar(im, ax=ax2, shrink=0.8)
        ax2.contour(xx, yy, nets, levels=[0],
                    colors=["black"], linewidths=2.5, linestyles="--")

        for pt in X_DATA:
            z_pt = w1 * pt[0] + w2 * pt[1] + b
            ax2.scatter(pt[0], pt[1], c="white",
                        s=180, edgecolors="black", linewidth=2, zorder=6)
            ax2.text(pt[0] + 0.06, pt[1] + 0.06,
                     f"z={z_pt:+.2f}", fontsize=8.5, color="#1a2634")

        ax2.set_xlim(xmin, xmax)
        ax2.set_ylim(ymin, ymax)
        ax2.set_xlabel("x₁", fontsize=11)
        ax2.set_ylabel("x₂", fontsize=11)
        ax2.set_title("순입력  z = w·x + b\n(양수 → 빨강, 음수 → 파랑)",
                      fontsize=11, fontweight="bold")
        ax2.grid(True, alpha=0.2)

        self._fig.tight_layout(pad=2.5)
        self._canvas.draw_idle()

    # ─────────────────────────────────────────
    # 프리셋 적용
    # ─────────────────────────────────────────
    def _apply_preset(self, w1: float, w2: float, b: float):
        self._w1_slider.set_value(w1)
        self._w2_slider.set_value(w2)
        self._b_slider.set_value(b)
        self._update_all()
