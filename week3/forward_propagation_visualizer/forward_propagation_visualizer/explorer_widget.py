"""explorer_widget.py — 순전파 탐색 탭"""
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QSlider, QLabel, QPushButton, QCheckBox, QSizePolicy,
)
from PySide6.QtCore import Qt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from network_model import SimpleNetwork
from styles import GROUP_STYLE, SLIDER_STYLE, PRIMARY_BTN, SECONDARY_BTN


class ExplorerWidget(QWidget):
    def __init__(self, network: SimpleNetwork, parent=None):
        super().__init__(parent)
        self._net = network
        self._seed_fixed = True
        self._seed_counter = 42

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # ── 좌 패널 ──────────────────────────────────
        left = QWidget()
        left.setFixedWidth(270)
        vl = QVBoxLayout(left)
        vl.setSpacing(8)

        grp_input = QGroupBox("입력값")
        grp_input.setStyleSheet(GROUP_STYLE)
        vi = QVBoxLayout(grp_input)
        for attr, label_text in (("_x1", "x₁"), ("_x2", "x₂")):
            lbl = QLabel(f"{label_text} = 0.00")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
            sl = QSlider(Qt.Horizontal)
            sl.setRange(-300, 300)
            sl.setValue(0 if attr == "_x1" else 0)
            sl.setStyleSheet(SLIDER_STYLE)
            setattr(self, attr + "_slider", sl)
            setattr(self, attr + "_label", lbl)
            vi.addWidget(lbl)
            vi.addWidget(sl)
        self._x1_slider.setValue(50)   # 0.5
        self._x2_slider.setValue(80)   # 0.8
        self._x1_slider.valueChanged.connect(self._on_x1)
        self._x2_slider.valueChanged.connect(self._on_x2)
        vl.addWidget(grp_input)

        self._seed_cb = QCheckBox("Seed 고정 (재현 가능)")
        self._seed_cb.setChecked(True)
        self._seed_cb.setStyleSheet("QCheckBox { font-size: 12px; color: #2c3e50; }")
        vl.addWidget(self._seed_cb)

        btn_rand = QPushButton("🎲 가중치 무작위")
        btn_rand.setStyleSheet(SECONDARY_BTN)
        btn_rand.clicked.connect(self._randomize)
        vl.addWidget(btn_rand)

        grp_out = QGroupBox("출력 결과")
        grp_out.setStyleSheet(GROUP_STYLE)
        vo = QVBoxLayout(grp_out)
        self._lbl_a2 = QLabel("출력 a₂ = —")
        self._lbl_a2.setAlignment(Qt.AlignCenter)
        self._lbl_a2.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #e74c3c; padding: 8px;"
        )
        self._lbl_z2 = QLabel("z₂ = —")
        self._lbl_z2.setAlignment(Qt.AlignCenter)
        self._lbl_z2.setStyleSheet("font-size: 13px; color: #636e72;")
        self._lbl_hidden = QLabel("")
        self._lbl_hidden.setStyleSheet("font-size: 12px; color: #2c3e50;")
        vo.addWidget(self._lbl_a2)
        vo.addWidget(self._lbl_z2)
        vo.addWidget(self._lbl_hidden)
        vl.addWidget(grp_out)
        vl.addStretch()
        layout.addWidget(left)

        # ── 우 캔버스 ─────────────────────────────────
        self._fig = Figure(figsize=(7, 4.5), tight_layout=True)
        self._ax_net = self._fig.add_subplot(1, 2, 1)
        self._ax_bar = self._fig.add_subplot(1, 2, 2)
        self._canvas = FigureCanvas(self._fig)
        layout.addWidget(self._canvas, 1)

        self._update()

    # ── 슬롯 ──────────────────────────────────────────
    def _on_x1(self, v):
        self._x1_label.setText(f"x₁ = {v/100:.2f}")
        self._update()

    def _on_x2(self, v):
        self._x2_label.setText(f"x₂ = {v/100:.2f}")
        self._update()

    def _randomize(self):
        if self._seed_cb.isChecked():
            self._seed_counter += 1
            self._net.randomize(self._seed_counter)
        else:
            self._net.randomize(None)
        self._update()
        # matrix_widget을 직접 업데이트하기 위해 시그널 불필요 — 부모가 공유 인스턴스 사용

    def _update(self):
        x1 = self._x1_slider.value() / 100.0
        x2 = self._x2_slider.value() / 100.0
        r = self._net.forward(x1, x2)

        self._lbl_a2.setText(f"출력 a₂ = {r.a2:.4f}")
        self._lbl_z2.setText(f"z₂ = {r.z2:.4f}")
        hidden_txt = "\n".join(
            f"h{i+1}: z={r.z1[i]:.3f} → a={r.a1[i]:.3f}" for i in range(3)
        )
        self._lbl_hidden.setText(hidden_txt)

        self._draw_network(x1, x2, r)
        self._draw_bar(r)
        self._canvas.draw_idle()

    def _draw_network(self, x1, x2, r):
        ax = self._ax_net
        ax.clear()
        ax.set_xlim(0, 4)
        ax.set_ylim(-0.5, 4.5)
        ax.axis("off")
        ax.set_title("뉴런 다이어그램 (활성화 강도)", fontsize=11, fontweight="bold")

        cmap = mcolors.LinearSegmentedColormap.from_list("bwr", ["#3498db","#ecf0f1","#e74c3c"])

        def norm_val(v, lo=-1.5, hi=1.5):
            return np.clip((v - lo) / (hi - lo), 0, 1)

        input_ys = [1.0, 3.0]
        hidden_ys = [0.5, 2.0, 3.5]
        output_y = 2.0

        # 연결선 (가중치 강도로 alpha)
        W1_max = np.abs(self._net.W1).max() + 1e-8
        for i, iy in enumerate(input_ys):
            for j, hy in enumerate(hidden_ys):
                w = self._net.W1[i, j]
                alpha = min(abs(w) / W1_max * 0.8 + 0.1, 0.9)
                color = "#e74c3c" if w > 0 else "#3498db"
                ax.plot([0.4, 1.6], [iy, hy], color=color, alpha=alpha, linewidth=1.2)

        W2_max = np.abs(self._net.W2).max() + 1e-8
        for j, hy in enumerate(hidden_ys):
            w = float(self._net.W2[j, 0])
            alpha = min(abs(w) / W2_max * 0.8 + 0.1, 0.9)
            color = "#e74c3c" if w > 0 else "#3498db"
            ax.plot([2.4, 3.4], [hy, output_y], color=color, alpha=alpha, linewidth=1.5)

        # 입력 뉴런
        for i, (iy, val) in enumerate(zip(input_ys, [x1, x2])):
            c = cmap(norm_val(val))
            circle = mpatches.Circle((0.2, iy), 0.2, color=c, ec="black", lw=1.5, zorder=5)
            ax.add_patch(circle)
            ax.text(0.2, iy, f"{val:.2f}", ha="center", va="center", fontsize=9, fontweight="bold")
            ax.text(0.2, iy - 0.38, f"x{i+1}", ha="center", fontsize=9, color="#636e72")

        # 은닉 뉴런
        for j, (hy, a, z) in enumerate(zip(hidden_ys, r.a1, r.z1)):
            c = cmap(norm_val(a, 0, 1))
            circle = mpatches.Circle((2.0, hy), 0.2, color=c, ec="black", lw=1.5, zorder=5)
            ax.add_patch(circle)
            ax.text(2.0, hy, f"{a:.2f}", ha="center", va="center", fontsize=9, fontweight="bold")
            ax.text(2.0, hy - 0.38, f"h{j+1}", ha="center", fontsize=9, color="#636e72")

        # 출력 뉴런
        c = cmap(norm_val(r.a2, 0, 1))
        circle = mpatches.Circle((3.6, output_y), 0.22, color=c, ec="black", lw=2, zorder=5)
        ax.add_patch(circle)
        ax.text(3.6, output_y, f"{r.a2:.3f}", ha="center", va="center", fontsize=10, fontweight="bold")
        ax.text(3.6, output_y - 0.45, "출력", ha="center", fontsize=9, color="#636e72")

        # 층 레이블
        ax.text(0.2, -0.3, "입력층", ha="center", fontsize=9, color="#2c3e50", fontweight="bold")
        ax.text(2.0, -0.3, "은닉층\n(ReLU)", ha="center", fontsize=9, color="#2c3e50", fontweight="bold")
        ax.text(3.6, -0.3, "출력층\n(Sigmoid)", ha="center", fontsize=9, color="#2c3e50", fontweight="bold")

    def _draw_bar(self, r):
        ax = self._ax_bar
        ax.clear()
        labels = [f"h{i+1}" for i in range(3)]
        x = np.arange(3)
        w = 0.35
        bars_z = ax.bar(x - w/2, r.z1, w, label="z₁ (ReLU 전)", color="#f39c12", alpha=0.85)
        bars_a = ax.bar(x + w/2, r.a1, w, label="a₁ (ReLU 후)", color="#2ecc71", alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylabel("값")
        ax.set_title("은닉층: z₁ vs a₁", fontsize=11, fontweight="bold")
        ax.legend(fontsize=9)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.grid(True, alpha=0.3, axis="y")
