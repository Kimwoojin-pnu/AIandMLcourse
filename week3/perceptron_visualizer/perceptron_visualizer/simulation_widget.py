"""
simulation_widget.py
학습 시뮬레이션 탭 — 에포크별 실시간 학습 애니메이션 + 시각화
"""
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QRadioButton, QSlider, QSpinBox, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QButtonGroup, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as mpatches

from perceptron_model import Perceptron
from utils import setup_korean_font, X_DATA, GATE_LABELS, GATE_DESC
from styles import (
    GROUP_STYLE, PRIMARY_BTN, SECONDARY_BTN, PAUSE_BTN,
    TABLE_STYLE, SLIDER_STYLE, RADIO_STYLE,
)

setup_korean_font()

# 에포크 슬라이더 속도 → 타이머 간격(ms) 매핑
_SPEED_INTERVALS = {1: 600, 2: 400, 3: 250, 4: 150, 5: 80,
                    6: 50,  7: 30,  8: 15,  9: 8,   10: 3}
_SPEED_LABELS    = {1: "매우 느림", 2: "느림", 3: "느림", 4: "보통",
                    5: "중간", 6: "빠름", 7: "빠름",
                    8: "매우 빠름", 9: "최고속", 10: "최고속"}


class SimulationWidget(QWidget):
    """학습 시뮬레이션 탭"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 상태
        self._gate        = "AND"
        self._epoch       = 0
        self._max_epochs  = 100
        self._perceptron  = Perceptron(learning_rate=0.1)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._step)

        self._build_ui()
        self._reset(init=True)

    # ─────────────────────────────────────────
    # UI 구성
    # ─────────────────────────────────────────
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(14)

        root.addWidget(self._build_left(), 0)
        root.addWidget(self._build_right(), 1)

    # ── 왼쪽 패널 ──────────────────────────────
    def _build_left(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(290)
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # 게이트 선택
        gate_grp = QGroupBox("논리 게이트 선택")
        gate_grp.setStyleSheet(GROUP_STYLE)
        g_layout = QVBoxLayout(gate_grp)
        self._gate_bg = QButtonGroup(self)
        for i, gate in enumerate(["AND", "OR", "XOR"]):
            rb = QRadioButton(gate)
            rb.setStyleSheet(RADIO_STYLE)
            rb.setChecked(gate == "AND")
            self._gate_bg.addButton(rb, i)
            g_layout.addWidget(rb)
        self._gate_bg.idToggled.connect(self._on_gate_toggled)
        layout.addWidget(gate_grp)

        # 게이트 설명 라벨
        self._gate_desc_label = QLabel()
        self._gate_desc_label.setWordWrap(True)
        self._gate_desc_label.setStyleSheet("""
            font-size: 11px; color: #555; padding: 4px 2px;
        """)
        layout.addWidget(self._gate_desc_label)

        # 하이퍼파라미터
        param_grp = QGroupBox("하이퍼파라미터")
        param_grp.setStyleSheet(GROUP_STYLE)
        p_layout = QVBoxLayout(param_grp)

        # 학습률 슬라이더
        lr_row = QVBoxLayout()
        lr_header = QHBoxLayout()
        lr_lbl = QLabel("학습률 η")
        lr_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #34495e;")
        self._lr_val_lbl = QLabel("0.10")
        self._lr_val_lbl.setStyleSheet("font-size: 12px; color: #2980b9; font-weight: bold;")
        lr_header.addWidget(lr_lbl)
        lr_header.addStretch()
        lr_header.addWidget(self._lr_val_lbl)
        lr_row.addLayout(lr_header)
        self._lr_slider = QSlider(Qt.Horizontal)
        self._lr_slider.setRange(1, 100)
        self._lr_slider.setValue(10)
        self._lr_slider.setStyleSheet(SLIDER_STYLE)
        self._lr_slider.valueChanged.connect(self._on_lr_changed)
        lr_row.addWidget(self._lr_slider)
        lr_range = QHBoxLayout()
        for t in ["0.01", "", "0.50", "", "1.00"]:
            l = QLabel(t)
            l.setStyleSheet("font-size: 9px; color: #95a5a6;")
            l.setAlignment(Qt.AlignCenter)
            lr_range.addWidget(l, 0 if t else 1)
        lr_row.addLayout(lr_range)
        p_layout.addLayout(lr_row)

        # 에포크 수
        epoch_row = QHBoxLayout()
        epoch_lbl = QLabel("에포크 수")
        epoch_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #34495e;")
        self._epoch_spin = QSpinBox()
        self._epoch_spin.setRange(10, 2000)
        self._epoch_spin.setValue(100)
        self._epoch_spin.setSingleStep(10)
        self._epoch_spin.setFixedWidth(80)
        epoch_row.addWidget(epoch_lbl)
        epoch_row.addStretch()
        epoch_row.addWidget(self._epoch_spin)
        p_layout.addLayout(epoch_row)

        # 애니메이션 속도
        spd_row = QVBoxLayout()
        spd_header = QHBoxLayout()
        spd_lbl = QLabel("애니메이션 속도")
        spd_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #34495e;")
        self._spd_val_lbl = QLabel("중간")
        self._spd_val_lbl.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        spd_header.addWidget(spd_lbl)
        spd_header.addStretch()
        spd_header.addWidget(self._spd_val_lbl)
        spd_row.addLayout(spd_header)
        self._spd_slider = QSlider(Qt.Horizontal)
        self._spd_slider.setRange(1, 10)
        self._spd_slider.setValue(5)
        self._spd_slider.setStyleSheet(SLIDER_STYLE)
        self._spd_slider.valueChanged.connect(self._on_speed_changed)
        spd_row.addWidget(self._spd_slider)
        p_layout.addLayout(spd_row)

        layout.addWidget(param_grp)

        # 버튼
        self._train_btn = QPushButton("▶  학습 시작")
        self._train_btn.setStyleSheet(PRIMARY_BTN)
        self._train_btn.clicked.connect(self._on_train_clicked)
        self._reset_btn = QPushButton("↺  초기화")
        self._reset_btn.setStyleSheet(SECONDARY_BTN)
        self._reset_btn.clicked.connect(lambda: self._reset())
        layout.addWidget(self._train_btn)
        layout.addWidget(self._reset_btn)

        # 상태 텍스트
        self._status_lbl = QLabel("준비됨")
        self._status_lbl.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 2px;")
        layout.addWidget(self._status_lbl)

        # 학습 로그 테이블
        log_grp = QGroupBox("학습 로그")
        log_grp.setStyleSheet(GROUP_STYLE)
        log_layout = QVBoxLayout(log_grp)
        self._log_table = QTableWidget(0, 5)
        self._log_table.setHorizontalHeaderLabels(["에포크", "w₁", "w₂", "b", "정확도"])
        self._log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._log_table.verticalHeader().setVisible(False)
        self._log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._log_table.setStyleSheet(TABLE_STYLE)
        self._log_table.setMaximumHeight(200)
        log_layout.addWidget(self._log_table)
        layout.addWidget(log_grp)

        layout.addStretch()
        return panel

    # ── 오른쪽 패널 ─────────────────────────────
    def _build_right(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 에포크 진행 표시
        self._epoch_bar_label = QLabel("에포크:  0  /  0")
        self._epoch_bar_label.setAlignment(Qt.AlignCenter)
        self._epoch_bar_label.setStyleSheet("""
            font-size: 14px; font-weight: bold; color: #2c3e50;
            background: #ecf0f1; border-radius: 5px;
            padding: 8px;
        """)
        layout.addWidget(self._epoch_bar_label)

        # Matplotlib 캔버스
        self._fig = Figure(figsize=(10, 5), dpi=85, facecolor="white")
        self._canvas = FigureCanvas(self._fig)
        self._canvas.setStyleSheet("border: 1px solid #dee2e6; border-radius: 4px;")
        layout.addWidget(self._canvas)

        return panel

    # ─────────────────────────────────────────
    # 이벤트 핸들러
    # ─────────────────────────────────────────
    def _on_gate_toggled(self, btn_id: int, checked: bool):
        if checked:
            self._gate = ["AND", "OR", "XOR"][btn_id]
            self._reset()

    def _on_lr_changed(self, value: int):
        lr = value / 100.0
        self._lr_val_lbl.setText(f"{lr:.2f}")
        self._perceptron.lr = lr

    def _on_speed_changed(self, value: int):
        self._spd_val_lbl.setText(_SPEED_LABELS[value])
        if self._timer.isActive():
            self._timer.setInterval(_SPEED_INTERVALS[value])

    def _on_train_clicked(self):
        if self._timer.isActive():
            self._timer.stop()
            self._train_btn.setText("▶  학습 재개")
            self._train_btn.setStyleSheet(PRIMARY_BTN)
            self._status_lbl.setText("일시 정지됨")
        else:
            if self._epoch >= self._max_epochs:
                self._reset(soft=True)
            self._max_epochs = self._epoch_spin.value()
            interval = _SPEED_INTERVALS[self._spd_slider.value()]
            self._timer.setInterval(interval)
            self._timer.start()
            self._train_btn.setText("⏸  일시 정지")
            self._train_btn.setStyleSheet(PAUSE_BTN)
            self._status_lbl.setText("학습 중…")

    # ─────────────────────────────────────────
    # 학습 스텝 (타이머 콜백)
    # ─────────────────────────────────────────
    def _step(self):
        if self._epoch >= self._max_epochs:
            self._finish()
            return

        y = GATE_LABELS[self._gate]
        acc = self._perceptron.train_one_epoch(X_DATA, y)
        self._epoch += 1

        self._epoch_bar_label.setText(
            f"에포크:  {self._epoch}  /  {self._max_epochs}"
        )

        # 로그 테이블 — 매 에포크 추가 (최대 표시는 스크롤)
        row = self._log_table.rowCount()
        self._log_table.insertRow(row)
        h = self._perceptron.history[-1]
        for col, val in enumerate([
            str(self._epoch),
            f"{h['w1']:+.3f}",
            f"{h['w2']:+.3f}",
            f"{h['bias']:+.3f}",
            f"{acc*100:.0f}%",
        ]):
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignCenter)
            if col == 4:
                c = QColor("#27ae60") if acc == 1.0 else QColor("#e74c3c")
                item.setForeground(c)
                if acc == 1.0:
                    item.setFont(QFont("", -1, QFont.Bold))
            self._log_table.setItem(row, col, item)
        self._log_table.scrollToBottom()

        self._draw()

        # 수렴 조기 종료 (XOR은 수렴 안 함 → 만료까지 진행)
        if acc == 1.0 and self._gate != "XOR":
            self._finish(converged=True)

    def _finish(self, converged: bool = False):
        self._timer.stop()
        self._train_btn.setText("▶  학습 시작")
        self._train_btn.setStyleSheet(PRIMARY_BTN)

        if converged:
            self._status_lbl.setText(
                f"✅ 수렴 완료! (에포크 {self._epoch}, 정확도 100%)"
            )
            self._status_lbl.setStyleSheet("font-size: 12px; color: #27ae60; font-weight: bold;")
        elif self._gate == "XOR" and self._epoch >= self._max_epochs:
            last_acc = self._perceptron.history[-1]["accuracy"] * 100
            self._status_lbl.setText(
                f"⚠️ XOR 해결 불가! 최종 정확도: {last_acc:.0f}% (단층 한계)"
            )
            self._status_lbl.setStyleSheet("font-size: 12px; color: #e74c3c; font-weight: bold;")
        else:
            self._status_lbl.setText(f"완료 (에포크 {self._epoch})")
            self._status_lbl.setStyleSheet("font-size: 12px; color: #7f8c8d;")

    # ─────────────────────────────────────────
    # 초기화
    # ─────────────────────────────────────────
    def _reset(self, init: bool = False, soft: bool = False):
        self._timer.stop()
        self._train_btn.setText("▶  학습 시작")
        self._train_btn.setStyleSheet(PRIMARY_BTN)

        lr = self._lr_slider.value() / 100.0
        self._perceptron = Perceptron(learning_rate=lr)
        self._epoch = 0
        self._max_epochs = self._epoch_spin.value()

        self._epoch_bar_label.setText("에포크:  0  /  0")
        self._status_lbl.setText("준비됨")
        self._status_lbl.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        self._log_table.setRowCount(0)
        self._gate_desc_label.setText(GATE_DESC.get(self._gate, ""))

        self._draw()

    # ─────────────────────────────────────────
    # 시각화
    # ─────────────────────────────────────────
    def _draw(self):
        self._fig.clear()
        ax1 = self._fig.add_subplot(1, 2, 1)
        ax2 = self._fig.add_subplot(1, 2, 2)
        self._draw_boundary(ax1)
        self._draw_accuracy(ax2)
        self._fig.tight_layout(pad=2.5)
        self._canvas.draw_idle()

    def _draw_boundary(self, ax):
        y = GATE_LABELS[self._gate]
        xmin, xmax, ymin, ymax = -0.5, 1.5, -0.5, 1.5

        xx, yy = np.meshgrid(
            np.linspace(xmin, xmax, 250),
            np.linspace(ymin, ymax, 250),
        )
        # 빠른 배치 계산
        nets = (self._perceptron.w1 * xx +
                self._perceptron.w2 * yy +
                self._perceptron.b)
        Z = (nets >= 0).astype(int)

        ax.contourf(xx, yy, Z, alpha=0.18,
                    levels=[-0.5, 0.5, 1.5],
                    colors=["#3498db", "#e74c3c"])
        try:
            ax.contour(xx, yy, Z, levels=[0.5],
                       colors=["#2c3e50"], linewidths=2.0, linestyles="--")
        except Exception:
            pass

        # 데이터 포인트
        for i, (pt, lbl) in enumerate(zip(X_DATA, y)):
            color  = "#e74c3c" if lbl == 1 else "#3498db"
            marker = "o"       if lbl == 1 else "s"
            pred   = self._perceptron.predict_single(pt)
            edge   = "gold" if pred != lbl else "black"
            ax.scatter(pt[0], pt[1], c=color, marker=marker,
                       s=220, edgecolors=edge, linewidth=2.2, zorder=6)
            ax.text(pt[0] + 0.07, pt[1] + 0.07,
                    f"({int(pt[0])},{int(pt[1])})\n→{lbl}",
                    fontsize=8.5, color="#2c3e50")

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_xlabel("x₁", fontsize=11)
        ax.set_ylabel("x₂", fontsize=11)
        ax.set_title(f"{self._gate} 게이트 — 결정 경계", fontsize=12, fontweight="bold")
        ax.grid(True, alpha=0.25)

        patches = [
            mpatches.Patch(facecolor="#e74c3c", alpha=0.5, label="출력 = 1"),
            mpatches.Patch(facecolor="#3498db", alpha=0.5, label="출력 = 0"),
        ]
        ax.legend(handles=patches, loc="upper left", fontsize=9)

        # 현재 가중치 텍스트
        ax.text(0.02, 0.02,
                f"w₁={self._perceptron.w1:+.3f}  w₂={self._perceptron.w2:+.3f}  b={self._perceptron.b:+.3f}",
                transform=ax.transAxes, fontsize=8.5, color="#7f8c8d",
                verticalalignment="bottom")

    def _draw_accuracy(self, ax):
        if not self._perceptron.history:
            ax.text(0.5, 0.5, "학습을 시작하세요\n▶ 버튼을 클릭하세요",
                    ha="center", va="center", transform=ax.transAxes,
                    fontsize=12, color="#95a5a6", multialignment="center")
            ax.set_title("정확도 변화 (Accuracy)", fontsize=12, fontweight="bold")
            ax.set_xlim(0, 1)
            ax.set_ylim(-5, 110)
            ax.grid(True, alpha=0.25)
            return

        epochs = [h["epoch"]        for h in self._perceptron.history]
        accs   = [h["accuracy"]*100 for h in self._perceptron.history]

        ax.plot(epochs, accs, "-", color="#2980b9", linewidth=1.8, alpha=0.8)
        ax.fill_between(epochs, accs, alpha=0.08, color="#2980b9")
        ax.axhline(y=100, color="#27ae60", linestyle="--", alpha=0.5,
                   linewidth=1.2, label="100%")

        # 마지막 값 강조
        if accs:
            last_c = "#27ae60" if accs[-1] == 100 else "#e74c3c"
            ax.scatter([epochs[-1]], [accs[-1]], color=last_c, s=60, zorder=5)
            ax.annotate(f"{accs[-1]:.0f}%",
                        xy=(epochs[-1], accs[-1]),
                        xytext=(6, 4), textcoords="offset points",
                        fontsize=10, color=last_c, fontweight="bold")

        ax.set_ylim(-5, 110)
        ax.set_xlabel("에포크", fontsize=11)
        ax.set_ylabel("정확도 (%)", fontsize=11)
        ax.set_title("정확도 변화 (Accuracy)", fontsize=12, fontweight="bold")
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=9)
