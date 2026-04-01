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
        self.fig = Figure(facecolor=COLORS["panel"])
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
        axes_flat = (
            np.array(self.axes).flatten()
            if hasattr(self.axes, '__iter__')
            else [self.axes]
        )
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
        axes_flat = (
            np.array(self.axes).flatten()
            if hasattr(self.axes, '__iter__')
            else [self.axes]
        )
        for ax in axes_flat:
            ax.cla()
        self._apply_dark_all()

    def draw(self):
        self.canvas.draw_idle()
