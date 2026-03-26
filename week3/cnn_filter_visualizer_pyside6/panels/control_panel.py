from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                                QLabel, QPushButton, QSlider, QButtonGroup,
                                QRadioButton, QFrame)
from PySide6.QtCore import Qt
from logic.filters import FILTERS, FILTER_NAMES

K_POS_BG = "#E6F1FB";  K_POS_FG = "#0C447C"
K_NEG_BG = "#FAECE7";  K_NEG_FG = "#712B13"
K_ZER_BG = "#F0F0F0";  K_ZER_FG = "#888888"

PATCH_BG = "#E6F1FB"
PROD_POS = "#E2F0EB";  PROD_POS_FG = "#085041"
PROD_NEG = "#FAECE7";  PROD_NEG_FG = "#712B13"
PROD_ZER = "#F4F4F4";  PROD_ZER_FG = "#888888"

_CELL_CSS = "font-family:'Courier New'; font-size:9px; background:{bg}; color:{fg};"
_KERN_CSS = ("font-family:'Courier New'; font-size:12px; font-weight:bold;"
             " background:{bg}; color:{fg};")


def _cell_bg_fg(value, is_kernel=False):
    if value > 0:   return (K_POS_BG, K_POS_FG)
    elif value < 0: return (K_NEG_BG, K_NEG_FG)
    else:           return (K_ZER_BG, K_ZER_FG)


def _prod_bg_fg(value):
    if value > 0:   return (PROD_POS, PROD_POS_FG)
    elif value < 0: return (PROD_NEG, PROD_NEG_FG)
    else:           return (PROD_ZER, PROD_ZER_FG)


class ControlPanel(QWidget):
    def __init__(self, app, total_steps):
        super().__init__()
        self._app         = app
        self._total_steps = total_steps

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── 필터 선택 ──────────────────────────────────────────────
        layout.addWidget(self._head("필터 선택"))

        self._filter_group = QButtonGroup(self)
        for i, name in enumerate(FILTER_NAMES):
            row_w = QWidget()
            rl    = QHBoxLayout(row_w)
            rl.setContentsMargins(0, 1, 0, 1)
            rb = QRadioButton(name)
            rb.setStyleSheet("font-size:11px;")
            if i == 0:
                rb.setChecked(True)
            self._filter_group.addButton(rb, i)
            rl.addWidget(rb)
            desc = QLabel(f"  ({FILTERS[name]['desc']})")
            desc.setStyleSheet("font-size:8px; color:#999999;")
            rl.addWidget(desc)
            rl.addStretch()
            layout.addWidget(row_w)
        self._filter_group.idClicked.connect(self._on_filter_change)

        layout.addWidget(self._sep())

        # ── 커널 표시 ─────────────────────────────────────────────
        layout.addWidget(self._head("커널 (3×3)", 11))
        kern_w = QWidget()
        kern_g = QGridLayout(kern_w)
        kern_g.setSpacing(2)
        kern_g.setContentsMargins(0, 0, 0, 0)
        self._kernel_labels = [[None] * 3 for _ in range(3)]
        for r in range(3):
            for c in range(3):
                lbl = QLabel("0")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setFixedSize(38, 30)
                lbl.setStyleSheet(_KERN_CSS.format(bg=K_ZER_BG, fg=K_ZER_FG))
                kern_g.addWidget(lbl, r, c)
                self._kernel_labels[r][c] = lbl
        layout.addWidget(kern_w)
        layout.addSpacing(4)

        layout.addWidget(self._sep())

        # ── 계산식 표시 ───────────────────────────────────────────
        layout.addWidget(self._head("계산 과정 (현재 위치)", 11))

        self._pos_lbl = QLabel("")
        self._pos_lbl.setStyleSheet("font-size:9px; color:#555555;")
        layout.addWidget(self._pos_lbl)

        math_w = QWidget()
        math_l = QHBoxLayout(math_w)
        math_l.setContentsMargins(0, 4, 0, 4)
        math_l.setSpacing(4)
        self._patch_lbls, pw = self._make_3x3_grid()
        math_l.addWidget(pw)
        math_l.addWidget(self._op("×"))
        self._kcopy_lbls, kw = self._make_3x3_grid()
        math_l.addWidget(kw)
        math_l.addWidget(self._op("="))
        self._prod_lbls, prw = self._make_3x3_grid()
        math_l.addWidget(prw)
        math_l.addStretch()
        layout.addWidget(math_w)

        self._sum_lbl = QLabel("")
        self._sum_lbl.setStyleSheet("font-size:10px; color:#333333;")
        self._sum_lbl.setWordWrap(True)
        layout.addWidget(self._sum_lbl)

        self._out_lbl = QLabel("")
        self._out_lbl.setStyleSheet("font-size:14px; font-weight:bold; color:#0F6E56;")
        layout.addWidget(self._out_lbl)
        layout.addSpacing(4)

        layout.addWidget(self._sep())

        # ── 버튼 ─────────────────────────────────────────────────
        btn_row = QWidget()
        btn_l   = QHBoxLayout(btn_row)
        btn_l.setContentsMargins(0, 2, 0, 0)
        btn_l.setSpacing(6)

        self._reset_btn = self._btn("↺  Reset",  "#F0F0F0", "#444444")
        self._step_btn  = self._btn("Step  →",   "#DEEAF1", "#1A56A0")
        self._auto_btn  = self._btn("▶  Auto",   "#E2F0EB", "#085041")

        self._reset_btn.clicked.connect(self._app.reset)
        self._step_btn.clicked.connect(self._app.step)
        self._auto_btn.clicked.connect(self._app.toggle_auto)

        for b in [self._reset_btn, self._step_btn, self._auto_btn]:
            btn_l.addWidget(b)
        btn_l.addStretch()
        layout.addWidget(btn_row)

        # ── 속도 슬라이더 ─────────────────────────────────────────
        spd_row = QWidget()
        spd_l   = QHBoxLayout(spd_row)
        spd_l.setContentsMargins(0, 8, 0, 0)
        spd_lbl = QLabel("속도")
        spd_lbl.setStyleSheet("font-size:10px; color:#555555;")
        spd_l.addWidget(spd_lbl)

        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(1, 10)
        self._speed_slider.setValue(4)
        self._speed_slider.setFixedWidth(160)
        self._speed_slider.valueChanged.connect(lambda _: self._app.on_speed_change())
        spd_l.addWidget(self._speed_slider)

        hint = QLabel("느림 ← → 빠름")
        hint.setStyleSheet("font-size:8px; color:#AAAAAA;")
        spd_l.addWidget(hint)
        spd_l.addStretch()
        layout.addWidget(spd_row)

        layout.addWidget(self._sep())

        # ── 진행 표시 ─────────────────────────────────────────────
        self._progress_lbl = QLabel(f"0 / {self._total_steps:,}")
        self._progress_lbl.setStyleSheet("font-size:10px; color:#888888;")
        layout.addWidget(self._progress_lbl)

        # 초기화
        self.update_kernel_display(FILTER_NAMES[0])
        self.show_idle()

    # ── 레이아웃 헬퍼 ─────────────────────────────────────────────

    def _head(self, text, size=12):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"font-size:{size}px; font-weight:bold; color:#1A56A0; padding-top:4px;"
        )
        return lbl

    def _sep(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color:#EEEEEE; margin:6px 0;")
        return line

    def _op(self, text):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size:18px; color:#AAAAAA;")
        return lbl

    def _make_3x3_grid(self):
        widget = QWidget()
        grid   = QGridLayout(widget)
        grid.setSpacing(1)
        grid.setContentsMargins(0, 0, 0, 0)
        lbls = []
        for i in range(9):
            r, c = divmod(i, 3)
            lbl = QLabel("")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFixedSize(34, 22)
            lbl.setStyleSheet(_CELL_CSS.format(bg="#F0F0F0", fg="#333333"))
            grid.addWidget(lbl, r, c)
            lbls.append(lbl)
        return lbls, widget

    def _btn(self, text, bg, fg):
        b = QPushButton(text)
        b.setStyleSheet(
            f"QPushButton {{ background:{bg}; color:{fg}; border:none;"
            f" padding:7px 12px; font-size:11px; }}"
            f"QPushButton:hover {{ opacity:0.85; }}"
        )
        return b

    # ── 공개 API ──────────────────────────────────────────────────

    def get_filter_name(self):
        return FILTER_NAMES[self._filter_group.checkedId()]

    def get_speed(self):
        return self._speed_slider.value()

    def set_auto_btn_text(self, text):
        self._auto_btn.setText(text)

    def update_kernel_display(self, filter_name):
        kernel = FILTERS[filter_name]["kernel"]
        for r in range(3):
            for c in range(3):
                v      = kernel[r][c]
                bg, fg = _cell_bg_fg(v)
                self._kernel_labels[r][c].setText(str(v))
                self._kernel_labels[r][c].setStyleSheet(
                    _KERN_CSS.format(bg=bg, fg=fg)
                )

    def update_calc_display(self, result, row, col, mode):
        self._pos_lbl.setText(
            f"위치  행 {row},  열 {col}  →  Feature Map [{row}][{col}]"
        )

        for i, v in enumerate(result["patch"]):
            self._patch_lbls[i].setText(str(v))
            self._patch_lbls[i].setStyleSheet(
                _CELL_CSS.format(bg=PATCH_BG, fg="#0C447C")
            )

        for i, v in enumerate(result["kflat"]):
            bg, fg = _cell_bg_fg(v)
            self._kcopy_lbls[i].setText(str(v))
            self._kcopy_lbls[i].setStyleSheet(_CELL_CSS.format(bg=bg, fg=fg))

        for i, v in enumerate(result["products"]):
            bg, fg = _prod_bg_fg(v)
            self._prod_lbls[i].setText(str(v))
            self._prod_lbls[i].setStyleSheet(_CELL_CSS.format(bg=bg, fg=fg))

        raw  = result["raw_sum"]
        oval = result["output_val"]
        if mode == "abs":
            process = f"|{raw}| = {abs(raw)}  →  clamp(0,255) = {oval}"
        else:
            process = f"clamp(0, 255, {raw}) = {oval}"
        self._sum_lbl.setText(f"모두 더하면: {raw}    {process}")

        color = "#0F6E56" if oval > 180 else ("#1A56A0" if oval > 50 else "#993C1D")
        self._out_lbl.setText(f"출력값  →  {oval}")
        self._out_lbl.setStyleSheet(
            f"font-size:14px; font-weight:bold; color:{color};"
        )

    def show_idle(self):
        self._pos_lbl.setText("Step 버튼을 눌러 시작하세요.")
        for lbl in self._patch_lbls + self._kcopy_lbls + self._prod_lbls:
            lbl.setText("")
            lbl.setStyleSheet(_CELL_CSS.format(bg="#F0F0F0", fg="#333333"))
        self._sum_lbl.setText("")
        self._out_lbl.setText("")

    def update_progress(self, step_idx):
        if step_idx >= self._total_steps:
            self._progress_lbl.setText("완료! 다른 필터로 바꿔보세요.")
            self._progress_lbl.setStyleSheet("font-size:10px; color:#0F6E56;")
        else:
            self._progress_lbl.setText(f"{step_idx:,} / {self._total_steps:,}")
            self._progress_lbl.setStyleSheet("font-size:10px; color:#888888;")

    # ── 내부 ──────────────────────────────────────────────────────

    def _on_filter_change(self, idx):
        self.update_kernel_display(FILTER_NAMES[idx])
        self._app.on_filter_change()
