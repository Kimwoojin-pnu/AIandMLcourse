# shared/nn_diagram.py
# Custom QPainter widget: live neural-network architecture diagram
# Pulses during training via QTimer-driven opacity animation.

import math
import random
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient

from .colors import COLORS

_MAX_NODES_SHOWN = 7   # max circles per layer before truncating with "…"
_NODE_R = 5            # node radius px
_LAYER_GAP = 38        # horizontal gap between layers
_NODE_GAP = 14         # vertical gap between nodes


def _layer_ys(n: int, center_y: float) -> list[float]:
    """Return evenly-spaced y-coordinates for n nodes centred on center_y."""
    count = min(n, _MAX_NODES_SHOWN)
    total = (count - 1) * _NODE_GAP
    top = center_y - total / 2
    return [top + i * _NODE_GAP for i in range(count)]


class NNDiagramWidget(QWidget):
    """
    Renders a schematic of the network architecture and animates node
    'firing' while training is active.

    Call set_layers([in, h1, h2, ..., out]) to update the diagram.
    Call set_training(True/False) to start/stop the pulse animation.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layers: list[int] = [1, 64, 64, 1]
        self._training = False
        self._pulse_phase: list[list[float]] = []   # opacity 0.0–1.0 per node
        self._timer = QTimer(self)
        self._timer.setInterval(80)
        self._timer.timeout.connect(self._tick)
        self._rebuild_pulse()
        self.setMinimumHeight(110)

    # ── Public API ──────────────────────────────────────────────────────

    def set_layers(self, layer_sizes: list[int]):
        self._layers = layer_sizes
        self._rebuild_pulse()
        self.update()

    def set_training(self, active: bool):
        self._training = active
        if active:
            self._timer.start()
        else:
            self._timer.stop()
            self._reset_pulse()
            self.update()

    # ── Internal ────────────────────────────────────────────────────────

    def _rebuild_pulse(self):
        self._pulse_phase = [
            [random.random() for _ in range(min(n, _MAX_NODES_SHOWN))]
            for n in self._layers
        ]

    def _reset_pulse(self):
        for layer in self._pulse_phase:
            for i in range(len(layer)):
                layer[i] = 0.6

    def _tick(self):
        for layer in self._pulse_phase:
            for i in range(len(layer)):
                layer[i] = (layer[i] + random.uniform(0.05, 0.25)) % 1.0
        self.update()

    def paintEvent(self, event):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(0, 0, w, h, QColor(COLORS["bg"]))

        n_layers = len(self._layers)
        if n_layers == 0:
            return

        total_w = (n_layers - 1) * _LAYER_GAP
        x_start = (w - total_w) / 2
        cy = h / 2

        layer_xs = [x_start + i * _LAYER_GAP for i in range(n_layers)]
        layer_ys_all = [_layer_ys(n, cy) for n in self._layers]

        # Draw connections (behind nodes)
        pen_conn = QPen(QColor(COLORS["border_light"]))
        pen_conn.setWidthF(0.8)
        painter.setPen(pen_conn)
        for li in range(n_layers - 1):
            x0 = layer_xs[li]
            x1 = layer_xs[li + 1]
            for y0 in layer_ys_all[li]:
                for y1 in layer_ys_all[li + 1]:
                    painter.drawLine(
                        QPointF(x0 + _NODE_R, y0),
                        QPointF(x1 - _NODE_R, y1),
                    )

        # Draw nodes
        for li, (lx, ys, n) in enumerate(zip(layer_xs, layer_ys_all, self._layers)):
            for ni, ny in enumerate(ys):
                phase = self._pulse_phase[li][ni] if li < len(self._pulse_phase) and ni < len(self._pulse_phase[li]) else 0.6

                if self._training:
                    glow_alpha = int(40 + 180 * abs(math.sin(phase * math.pi)))
                else:
                    glow_alpha = 120

                # Glow halo
                grad = QRadialGradient(QPointF(lx, ny), _NODE_R * 3)
                glow_col = QColor(COLORS["accent"])
                glow_col.setAlpha(glow_alpha // 3)
                grad.setColorAt(0, glow_col)
                grad.setColorAt(1, QColor(0, 0, 0, 0))
                painter.setBrush(QBrush(grad))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(lx, ny), _NODE_R * 3, _NODE_R * 3)

                # Node fill
                node_col = QColor(COLORS["accent"])
                node_col.setAlpha(glow_alpha)
                painter.setBrush(QBrush(node_col))
                node_border = QColor(COLORS["accent"])
                node_border.setAlpha(min(255, glow_alpha + 60))
                painter.setPen(QPen(node_border, 1))
                painter.drawEllipse(QPointF(lx, ny), _NODE_R, _NODE_R)

            # Truncation ellipsis
            if n > _MAX_NODES_SHOWN:
                painter.setPen(QPen(QColor(COLORS["text_muted"])))
                f = QFont("Consolas", 7)
                painter.setFont(f)
                painter.drawText(
                    QRectF(lx - 12, cy + (_MAX_NODES_SHOWN / 2) * _NODE_GAP + 2, 24, 12),
                    Qt.AlignmentFlag.AlignCenter, "…",
                )

            # Layer size label (below diagram)
            painter.setPen(QPen(QColor(COLORS["text_muted"])))
            f2 = QFont("Consolas", 7)
            painter.setFont(f2)
            label_y = cy + (_MAX_NODES_SHOWN / 2) * _NODE_GAP + 14
            painter.drawText(
                QRectF(lx - 16, label_y, 32, 12),
                Qt.AlignmentFlag.AlignCenter,
                str(n),
            )

        painter.end()
