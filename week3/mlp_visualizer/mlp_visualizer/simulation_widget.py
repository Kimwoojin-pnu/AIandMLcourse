"""simulation_widget.py — XOR 학습 시뮬레이션"""
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QSlider, QLabel, QPushButton, QSpinBox, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from mlp_model import MLPModel
from utils import X_XOR, y_XOR
from styles import GROUP_STYLE, SLIDER_STYLE, PRIMARY_BTN, PAUSE_BTN, SECONDARY_BTN, TABLE_STYLE

_SPEED_MAP = {0: 200, 1: 100, 2: 50, 3: 20, 4: 10, 5: 3}
_STEPS_PER_TICK = {0: 1, 1: 2, 2: 5, 3: 10, 4: 50, 5: 100}


class SimulationWidget(QWidget):
    def __init__(self, model: MLPModel, gradient_refresh_cb=None, parent=None):
        super().__init__(parent)
        self._model = model
        self._grad_cb = gradient_refresh_cb
        self._running = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._step)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # ── 좌 패널 ──────────────────────────────────
        left = QWidget()
        left.setFixedWidth(290)
        vl = QVBoxLayout(left)
        vl.setSpacing(6)

        # 모델 설정
        grp_m = QGroupBox("모델 설정")
        grp_m.setStyleSheet(GROUP_STYLE)
        vm = QVBoxLayout(grp_m)
        vm.addWidget(QLabel("은닉 뉴런 수:"))
        self._hidden_spin = QSpinBox()
        self._hidden_spin.setRange(2, 16)
        self._hidden_spin.setValue(4)
        vm.addWidget(self._hidden_spin)
        vm.addWidget(QLabel("학습률 (η):"))
        self._lr_spin = QDoubleSpinBox()
        self._lr_spin.setRange(0.01, 2.0)
        self._lr_spin.setSingleStep(0.01)
        self._lr_spin.setValue(0.5)
        vm.addWidget(self._lr_spin)
        vl.addWidget(grp_m)

        # 학습 설정
        grp_t = QGroupBox("학습 설정")
        grp_t.setStyleSheet(GROUP_STYLE)
        vt = QVBoxLayout(grp_t)
        vt.addWidget(QLabel("총 에포크:"))
        self._epoch_spin = QSpinBox()
        self._epoch_spin.setRange(100, 50000)
        self._epoch_spin.setSingleStep(500)
        self._epoch_spin.setValue(10000)
        vt.addWidget(self._epoch_spin)
        vt.addWidget(QLabel("속도:"))
        self._speed_sl = QSlider(Qt.Horizontal)
        self._speed_sl.setRange(0, 5)
        self._speed_sl.setValue(3)
        self._speed_sl.setStyleSheet(SLIDER_STYLE)
        vt.addWidget(self._speed_sl)
        vl.addWidget(grp_t)

        # 버튼
        self._btn_start = QPushButton("▶ 학습 시작")
        self._btn_start.setStyleSheet(PRIMARY_BTN)
        self._btn_pause = QPushButton("⏸ 일시정지")
        self._btn_pause.setStyleSheet(PAUSE_BTN)
        self._btn_pause.setEnabled(False)
        self._btn_reset = QPushButton("↺ 초기화")
        self._btn_reset.setStyleSheet(SECONDARY_BTN)
        for b in (self._btn_start, self._btn_pause, self._btn_reset):
            vl.addWidget(b)
        self._btn_start.clicked.connect(self._start)
        self._btn_pause.clicked.connect(self._toggle_pause)
        self._btn_reset.clicked.connect(self._reset)

        # 상태 레이블
        self._status_lbl = QLabel("대기 중")
        self._status_lbl.setAlignment(Qt.AlignCenter)
        self._status_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #636e72; padding: 4px;")
        vl.addWidget(self._status_lbl)

        # 로그 테이블
        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["에포크", "Loss", "정확도"])
        self._table.setStyleSheet(TABLE_STYLE)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setMaximumHeight(200)
        vl.addWidget(self._table)
        vl.addStretch()
        layout.addWidget(left)

        # ── 우 캔버스 ─────────────────────────────────
        self._fig = Figure(figsize=(7, 4.5), tight_layout=True)
        self._ax_bound = self._fig.add_subplot(1, 2, 1)
        self._ax_loss  = self._fig.add_subplot(1, 2, 2)
        self._canvas = FigureCanvas(self._fig)
        layout.addWidget(self._canvas, 1)

        self._draw()

    # ── 슬롯 ──────────────────────────────────────────
    def _start(self):
        self._model.reset(
            hidden_size=self._hidden_spin.value(),
            lr=self._lr_spin.value()
        )
        self._table.setRowCount(0)
        self._running = True
        speed = self._speed_sl.value()
        self._timer.setInterval(_SPEED_MAP[speed])
        self._timer.start()
        self._btn_start.setEnabled(False)
        self._btn_pause.setEnabled(True)
        self._status_lbl.setText("학습 중...")
        self._status_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #2980b9; padding: 4px;")

    def _toggle_pause(self):
        if self._running:
            self._timer.stop()
            self._running = False
            self._btn_pause.setText("▶ 재개")
        else:
            self._timer.start()
            self._running = True
            self._btn_pause.setText("⏸ 일시정지")

    def _reset(self):
        self._timer.stop()
        self._running = False
        self._model.reset(self._hidden_spin.value(), self._lr_spin.value())
        self._table.setRowCount(0)
        self._btn_start.setEnabled(True)
        self._btn_pause.setEnabled(False)
        self._btn_pause.setText("⏸ 일시정지")
        self._status_lbl.setText("대기 중")
        self._status_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #636e72; padding: 4px;")
        self._draw()

    def _step(self):
        max_ep = self._epoch_spin.value()
        steps = _STEPS_PER_TICK[self._speed_sl.value()]
        for _ in range(steps):
            if self._model.epoch >= max_ep:
                break
            self._model.train_step(X_XOR, y_XOR)

        loss = self._model.loss_history[-1] if self._model.loss_history else 0
        acc  = self._model.accuracy(X_XOR, y_XOR)

        # 로그 (매 200 에포크마다)
        if self._model.epoch % 200 < steps:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(str(self._model.epoch)))
            self._table.setItem(row, 1, QTableWidgetItem(f"{loss:.6f}"))
            self._table.setItem(row, 2, QTableWidgetItem(f"{acc*100:.1f}%"))
            self._table.scrollToBottom()

        # 경사 위젯 갱신 (100 step마다)
        if self._model.epoch % 100 < steps and self._grad_cb:
            self._grad_cb()

        self._draw()

        if self._model.epoch >= max_ep or acc >= 1.0:
            self._timer.stop()
            self._running = False
            if acc >= 1.0:
                self._status_lbl.setText("✅ 학습 완료! XOR 100% 정확도 달성")
                self._status_lbl.setStyleSheet(
                    "font-size: 13px; font-weight: bold; color: #27ae60; padding: 4px;"
                )
            else:
                self._status_lbl.setText(f"완료 (최종 정확도 {acc*100:.1f}%)")
                self._status_lbl.setStyleSheet(
                    "font-size: 13px; font-weight: bold; color: #e67e22; padding: 4px;"
                )
            self._btn_start.setEnabled(True)
            self._btn_pause.setEnabled(False)

    def _draw(self):
        # 결정 경계
        ax = self._ax_bound
        ax.clear()
        xx, yy = np.meshgrid(np.linspace(-0.5, 1.5, 200), np.linspace(-0.5, 1.5, 200))
        Z = self._model.forward(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
        ax.contourf(xx, yy, Z, levels=20, cmap="RdYlBu", alpha=0.85)
        colors = ["blue", "red", "red", "blue"]
        for i, (pt, c) in enumerate(zip(X_XOR, colors)):
            ax.scatter(pt[0], pt[1], color=c, s=200, edgecolors="black", lw=2, zorder=5)
            ax.text(pt[0], pt[1]-0.14, f"({int(pt[0])},{int(pt[1])})", ha="center", fontsize=9)
        acc = self._model.accuracy(X_XOR, y_XOR)
        ax.set_title(f"XOR 결정 경계 (Epoch {self._model.epoch}, Acc {acc*100:.1f}%)",
                     fontsize=10, fontweight="bold")
        ax.set_xlim(-0.5, 1.5)
        ax.set_ylim(-0.5, 1.5)
        ax.grid(True, alpha=0.3)

        # Loss 곡선
        ax = self._ax_loss
        ax.clear()
        if self._model.loss_history:
            ax.plot(self._model.loss_history, linewidth=1.5, color="#2980b9")
            ax.set_yscale("log")
        ax.set_title("학습 Loss (MSE, log scale)", fontsize=10, fontweight="bold")
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss")
        ax.grid(True, alpha=0.3)
        self._canvas.draw_idle()
