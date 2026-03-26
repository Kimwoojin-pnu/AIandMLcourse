from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                                QLabel, QFrame)
from PySide6.QtCore import QTimer
from panels.input_panel import InputPanel
from panels.control_panel import ControlPanel
from panels.output_panel import OutputPanel
from logic.convolution import compute_one
from logic.filters import FILTERS
from utils.image_loader import IMG_N

OUT_N       = IMG_N - 2
TOTAL_STEPS = OUT_N * OUT_N


class MainWindow(QMainWindow):
    TOTAL_STEPS = TOTAL_STEPS
    OUT_N       = OUT_N

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CNN 합성곱 필터 시각화  |  MIT 6.S191 Lecture 3")
        self.setMinimumSize(1080, 700)

        self._step_idx    = 0
        self._auto_running = False
        self._auto_timer  = QTimer(self)
        self._auto_timer.setSingleShot(True)
        self._auto_timer.timeout.connect(self._auto_batch)
        self._feature_map = [[None] * OUT_N for _ in range(OUT_N)]

        central = QWidget()
        self.setCentralWidget(central)
        vbox = QVBoxLayout(central)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        # ── 헤더 ────────────────────────────────────────────────
        header = QLabel(
            "  CNN 합성곱 필터 시각화   |   MIT 6.S191 Introduction to Deep Learning  —  Lecture 3"
        )
        header.setStyleSheet(
            "background:#1A56A0; color:#FFFFFF; font-size:13px; font-weight:bold; padding:10px;"
        )
        vbox.addWidget(header)

        # ── 패널 영역 ────────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet("background:#F0F4F8;")
        hbox = QHBoxLayout(content)
        hbox.setContentsMargins(16, 12, 16, 12)
        hbox.setSpacing(8)
        vbox.addWidget(content, stretch=1)

        self.input_panel   = InputPanel(on_change_callback=self.on_input_change)
        self.control_panel = ControlPanel(app=self, total_steps=TOTAL_STEPS)
        self.output_panel  = OutputPanel()

        # 입력·출력 패널은 고정 폭, 컨트롤 패널은 유동
        for panel, stretch in [(self.input_panel, 0),
                               (self.control_panel, 1),
                               (self.output_panel, 0)]:
            card = self._make_card()
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(0, 0, 0, 0)
            card_layout.addWidget(panel)
            hbox.addWidget(card, stretch=stretch)

        # ── 푸터 ────────────────────────────────────────────────
        footer_text = (
            f"{IMG_N}×{IMG_N} 입력  |  3×3 필터  |  Stride=1  |  Valid Convolution"
            f"  →  {OUT_N}×{OUT_N} Feature Map ({TOTAL_STEPS:,}스텝)"
            "   |   introtodeeplearning.com"
        )
        footer = QLabel(footer_text)
        footer.setStyleSheet(
            "background:#EEEEEE; color:#888888; font-size:9px; padding:6px;"
        )
        vbox.addWidget(footer)

    # ── 레이아웃 헬퍼 ────────────────────────────────────────────

    @staticmethod
    def _make_card():
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background:#FFFFFF; border:1px solid #D8D8D8; border-radius:4px; }"
        )
        return frame

    # ── 이벤트 핸들러 ────────────────────────────────────────────

    def on_input_change(self):
        self.reset()

    def on_filter_change(self):
        self.reset()

    def on_speed_change(self):
        pass  # _auto_batch가 매 호출마다 슬라이더 값을 읽으므로 별도 처리 불필요

    # ── 핵심 로직 ────────────────────────────────────────────────

    def step(self):
        """수동 Step: 한 위치 합성곱 실행 + 즉시 UI 갱신."""
        if self._step_idx >= TOTAL_STEPS:
            return

        row, col = divmod(self._step_idx, OUT_N)
        pixels   = self.input_panel.get_pixels()
        fname    = self.control_panel.get_filter_name()
        kernel   = FILTERS[fname]["kernel"]
        mode     = FILTERS[fname]["mode"]

        result = compute_one(pixels, kernel, row, col, mode)
        self._feature_map[row][col] = result["output_val"]

        self.input_panel.highlight(row, col)
        self.output_panel.set_value(row, col, result["output_val"])
        self.output_panel.highlight(row, col)
        self.control_panel.update_calc_display(result, row, col, mode)

        self._step_idx += 1
        self.control_panel.update_progress(self._step_idx)

        if self._step_idx >= TOTAL_STEPS:
            self.input_panel.clear_highlight()
            self.output_panel.clear_highlight()
            self._auto_running = False
            self.control_panel.set_auto_btn_text("▶  Auto")

    def toggle_auto(self):
        if self._auto_running:
            self._cancel_auto()
            self.control_panel.set_auto_btn_text("▶  Auto")
        else:
            if self._step_idx >= TOTAL_STEPS:
                self.reset()
            self._auto_running = True
            self.control_panel.set_auto_btn_text("⏸  일시정지")
            self._auto_batch()

    def _auto_batch(self):
        """Auto 모드: 속도에 따라 여러 스텝을 한 프레임에 묶어 처리."""
        if not self._auto_running or self._step_idx >= TOTAL_STEPS:
            self._auto_running = False
            self.control_panel.set_auto_btn_text("▶  Auto")
            return

        speed           = self.control_panel.get_speed()
        steps_per_frame = speed * speed           # 1 ~ 100
        delay           = max(16, 500 // speed)   # 50 ~ 500 ms

        pixels = self.input_panel.get_pixels()
        fname  = self.control_panel.get_filter_name()
        kernel = FILTERS[fname]["kernel"]
        mode   = FILTERS[fname]["mode"]

        last_result      = None
        last_row = last_col = 0

        for _ in range(steps_per_frame):
            if self._step_idx >= TOTAL_STEPS:
                break
            row, col = divmod(self._step_idx, OUT_N)
            result   = compute_one(pixels, kernel, row, col, mode)
            self._feature_map[row][col] = result["output_val"]
            self.output_panel.put_value(row, col, result["output_val"])
            last_result      = result
            last_row, last_col = row, col
            self._step_idx  += 1

        self.output_panel.refresh()
        self.input_panel.highlight(last_row, last_col)
        self.output_panel.highlight(last_row, last_col)
        self.control_panel.update_calc_display(last_result, last_row, last_col, mode)
        self.control_panel.update_progress(self._step_idx)

        if self._step_idx >= TOTAL_STEPS:
            self.input_panel.clear_highlight()
            self.output_panel.clear_highlight()
            self._auto_running = False
            self.control_panel.set_auto_btn_text("▶  Auto")
        else:
            self._auto_timer.start(delay)

    def _cancel_auto(self):
        self._auto_running = False
        self._auto_timer.stop()

    def reset(self):
        """전체 초기화."""
        self._cancel_auto()
        self._step_idx    = 0
        self._feature_map = [[None] * OUT_N for _ in range(OUT_N)]
        self.input_panel.clear_highlight()
        self.output_panel.clear()
        self.control_panel.update_progress(0)
        self.control_panel.show_idle()
        self.control_panel.set_auto_btn_text("▶  Auto")
