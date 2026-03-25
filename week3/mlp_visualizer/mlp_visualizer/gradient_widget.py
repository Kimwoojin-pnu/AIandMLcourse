"""gradient_widget.py — 경사 시각화 탭"""
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from mlp_model import MLPModel
from utils import X_XOR, y_XOR


class GradientWidget(QWidget):
    def __init__(self, model: MLPModel, parent=None):
        super().__init__(parent)
        self._model = model
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        self._fig = Figure(figsize=(8, 5), tight_layout=True)
        self._canvas = FigureCanvas(self._fig)
        layout.addWidget(self._canvas)
        self.refresh()

    def refresh(self):
        self._fig.clear()
        m = self._model
        axes = self._fig.subplots(2, 2)

        # dW1
        ax = axes[0, 0]
        dw1 = m.dW1 if m.dW1 is not None else np.zeros((2, m.hidden_size))
        im = ax.imshow(dw1, cmap="RdBu_r", aspect="auto")
        self._fig.colorbar(im, ax=ax, shrink=0.8)
        ax.set_title("dW₁ (입력→은닉 경사)", fontsize=10, fontweight="bold")
        ax.set_ylabel("입력 뉴런")
        ax.set_xlabel("은닉 뉴런")

        # dW2
        ax = axes[0, 1]
        dw2 = m.dW2 if m.dW2 is not None else np.zeros((m.hidden_size, 1))
        im2 = ax.imshow(dw2, cmap="RdBu_r", aspect="auto")
        self._fig.colorbar(im2, ax=ax, shrink=0.8)
        ax.set_title("dW₂ (은닉→출력 경사)", fontsize=10, fontweight="bold")
        ax.set_ylabel("은닉 뉴런")

        # 경사 크기 막대
        ax = axes[1, 0]
        w1_norm = float(np.linalg.norm(dw1)) if m.dW1 is not None else 0
        w2_norm = float(np.linalg.norm(dw2)) if m.dW2 is not None else 0
        bars = ax.bar(["||dW₁||", "||dW₂||"], [w1_norm, w2_norm],
                      color=["#3498db", "#e74c3c"], alpha=0.85)
        for bar, val in zip(bars, [w1_norm, w2_norm]):
            ax.text(bar.get_x() + bar.get_width()/2, val + 0.0001,
                    f"{val:.4f}", ha="center", va="bottom", fontsize=10)
        ax.set_title("레이어별 경사 크기 (Frobenius norm)", fontsize=10, fontweight="bold")
        ax.set_ylabel("||dW||")
        ax.grid(True, alpha=0.3, axis="y")

        # 은닉층 활성화 히트맵
        ax = axes[1, 1]
        if m.a1 is not None:
            im3 = ax.imshow(m.a1.T, cmap="viridis", aspect="auto", vmin=0, vmax=1)
            self._fig.colorbar(im3, ax=ax, shrink=0.8)
            ax.set_xticks(range(4))
            ax.set_xticklabels(["(0,0)", "(0,1)", "(1,0)", "(1,1)"])
            ax.set_yticks(range(m.hidden_size))
            ax.set_yticklabels([f"h{i+1}" for i in range(m.hidden_size)])
            for i in range(m.hidden_size):
                for j in range(4):
                    ax.text(j, i, f"{m.a1[j,i]:.2f}", ha="center", va="center",
                            color="white", fontsize=8, fontweight="bold")
        ax.set_title("은닉층 활성화 (4 XOR 샘플)", fontsize=10, fontweight="bold")
        ax.set_xlabel("XOR 입력 패턴")

        self._canvas.draw_idle()
