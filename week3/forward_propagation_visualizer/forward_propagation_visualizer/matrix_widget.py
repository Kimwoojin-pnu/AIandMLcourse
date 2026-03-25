"""matrix_widget.py — 행렬 시각화 탭"""
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from network_model import SimpleNetwork
from styles import SECONDARY_BTN


class MatrixWidget(QWidget):
    def __init__(self, network: SimpleNetwork, parent=None):
        super().__init__(parent)
        self._net = network

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # 상단 버튼
        btn_rand = QPushButton("🎲 가중치 무작위")
        btn_rand.setStyleSheet(SECONDARY_BTN)
        btn_rand.setFixedWidth(180)
        btn_rand.clicked.connect(self._randomize)

        hl = QHBoxLayout()
        hl.addWidget(btn_rand)
        hl.addStretch()
        layout.addLayout(hl)

        self._fig = Figure(figsize=(8, 5), tight_layout=True)
        self._canvas = FigureCanvas(self._fig)
        layout.addWidget(self._canvas, 1)

        self.refresh()

    def _randomize(self):
        self._net.randomize(None)
        self.refresh()

    def refresh(self):
        self._fig.clear()
        net = self._net
        r = net.forward(0.5, 0.8)   # 고정 샘플로 계산

        axes = self._fig.subplots(2, 2)

        # W1 히트맵
        ax = axes[0, 0]
        im = ax.imshow(net.W1, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
        self._fig.colorbar(im, ax=ax, shrink=0.8)
        ax.set_title("W₁ (2×3 가중치)", fontsize=11, fontweight="bold")
        ax.set_xlabel("은닉 뉴런")
        ax.set_ylabel("입력 뉴런")
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(["h1", "h2", "h3"])
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["x1", "x2"])
        for i in range(2):
            for j in range(3):
                ax.text(j, i, f"{net.W1[i,j]:.2f}", ha="center", va="center", fontsize=10, fontweight="bold")

        # W2 히트맵
        ax = axes[0, 1]
        im2 = ax.imshow(net.W2, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
        self._fig.colorbar(im2, ax=ax, shrink=0.8)
        ax.set_title("W₂ (3×1 가중치)", fontsize=11, fontweight="bold")
        ax.set_xlabel("출력 뉴런")
        ax.set_ylabel("은닉 뉴런")
        ax.set_xticks([0])
        ax.set_xticklabels(["출력"])
        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(["h1", "h2", "h3"])
        for i in range(3):
            ax.text(0, i, f"{net.W2[i,0]:.2f}", ha="center", va="center", fontsize=10, fontweight="bold")

        # z1 vs a1 막대
        ax = axes[1, 0]
        x = np.arange(3)
        w = 0.35
        ax.bar(x - w/2, r.z1, w, label="z₁ (ReLU 전)", color="#f39c12", alpha=0.85)
        ax.bar(x + w/2, r.a1, w, label="a₁ (ReLU 후)", color="#2ecc71", alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(["h1", "h2", "h3"])
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title("Layer 1 활성화 (x₁=0.5, x₂=0.8)", fontsize=10, fontweight="bold")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis="y")

        # z2 / a2 수평 막대
        ax = axes[1, 1]
        categories = ["z₂ (Sigmoid 전)", "a₂ (출력)"]
        values = [r.z2, r.a2]
        colors = ["#f39c12", "#e74c3c"]
        bars = ax.barh(categories, values, color=colors, alpha=0.85)
        for bar, val in zip(bars, values):
            ax.text(val + 0.02, bar.get_y() + bar.get_height()/2,
                    f"{val:.4f}", va="center", fontsize=11, fontweight="bold")
        ax.set_title("Layer 2 출력", fontsize=11, fontweight="bold")
        ax.set_xlim(min(values) - 0.5, max(values) + 0.8)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.grid(True, alpha=0.3, axis="x")

        self._canvas.draw_idle()
