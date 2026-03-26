import tkinter as tk
from panels.input_panel   import InputPanel
from panels.control_panel import ControlPanel
from panels.output_panel  import OutputPanel
from logic.convolution    import compute_one
from logic.filters        import FILTERS
from utils.image_loader   import IMG_N

OUT_N       = IMG_N - 2       # 126  (Valid Convolution 출력 크기)
TOTAL_STEPS = OUT_N * OUT_N   # 15,876


class App(tk.Tk):
    TOTAL_STEPS = TOTAL_STEPS
    OUT_N       = OUT_N

    def __init__(self):
        super().__init__()
        self.title("CNN 합성곱 필터 시각화  |  MIT 6.S191 Lecture 3")
        self.resizable(True, True)
        self.configure(bg="#F0F4F8")
        self.minsize(1080, 700)

        self._step_idx    = 0
        self._auto_id     = None
        self._feature_map = [[None] * OUT_N for _ in range(OUT_N)]

        self._build_header()
        self._build_panels()
        self._build_footer()

    # ── 레이아웃 ────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self, bg="#1A56A0", pady=10)
        hdr.pack(fill="x")
        tk.Label(
            hdr,
            text="  CNN 합성곱 필터 시각화   |   MIT 6.S191 Introduction to Deep Learning  —  Lecture 3",
            font=("Arial", 12, "bold"),
            bg="#1A56A0", fg="#FFFFFF",
        ).pack(side="left", padx=16)

    def _build_panels(self):
        container = tk.Frame(self, bg="#F0F4F8")
        container.pack(fill="both", expand=True, padx=16, pady=12)
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.columnconfigure(2, weight=0)

        left_card = self._make_card(container)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.input_panel = InputPanel(left_card, on_change_callback=self.on_input_change)
        self.input_panel.pack(fill="both", expand=True)

        mid_card = self._make_card(container)
        mid_card.grid(row=0, column=1, sticky="nsew", padx=(0, 8))
        self.control_panel = ControlPanel(mid_card, app=self, total_steps=self.TOTAL_STEPS)
        self.control_panel.pack(fill="both", expand=True)

        right_card = self._make_card(container)
        right_card.grid(row=0, column=2, sticky="nsew")
        self.output_panel = OutputPanel(right_card)
        self.output_panel.pack(fill="both", expand=True)

    def _build_footer(self):
        ftr = tk.Frame(self, bg="#EEEEEE", pady=6)
        ftr.pack(fill="x", side="bottom")
        tk.Label(
            ftr,
            text=(
                f"{IMG_N}×{IMG_N} 입력  |  3×3 필터  |  Stride=1  |  Valid Convolution"
                f"  →  {OUT_N}×{OUT_N} Feature Map ({TOTAL_STEPS:,}스텝)"
                "   |   introtodeeplearning.com"
            ),
            font=("Arial", 9),
            bg="#EEEEEE", fg="#888888",
        ).pack()

    @staticmethod
    def _make_card(parent):
        return tk.Frame(
            parent,
            bg="#FFFFFF",
            highlightthickness=1,
            highlightbackground="#D8D8D8",
            relief="flat",
        )

    # ── 이벤트 핸들러 ──────────────────────────────────────────

    def on_input_change(self):
        self.reset()

    def on_filter_change(self):
        self.reset()

    def on_speed_change(self):
        pass  # _auto_batch()가 매 호출마다 speed_var를 읽으므로 별도 처리 불필요

    # ── 핵심 로직 ───────────────────────────────────────────────

    def step(self):
        """수동 Step: 한 위치 합성곱 실행 + 즉시 UI 갱신."""
        if self._step_idx >= self.TOTAL_STEPS:
            return

        row, col   = divmod(self._step_idx, OUT_N)
        pixels     = self.input_panel.get_pixels()
        fname      = self.control_panel.filter_var.get()
        kernel     = FILTERS[fname]["kernel"]
        mode       = FILTERS[fname]["mode"]

        result = compute_one(pixels, kernel, row, col, mode)
        self._feature_map[row][col] = result["output_val"]

        self.input_panel.highlight(row, col)
        self.output_panel.set_value(row, col, result["output_val"])   # 즉시 갱신
        self.output_panel.highlight(row, col)
        self.control_panel.update_calc_display(result, row, col, mode)

        self._step_idx += 1
        self.control_panel.update_progress(self._step_idx)

        if self._step_idx >= self.TOTAL_STEPS:
            self.input_panel.clear_highlight()
            self.output_panel.clear_highlight()
            self._cancel_auto()
            self.control_panel.auto_btn.config(text="▶  Auto")

    def toggle_auto(self):
        if self._auto_id is not None:
            self._cancel_auto()
            self.control_panel.auto_btn.config(text="▶  Auto")
        else:
            if self._step_idx >= self.TOTAL_STEPS:
                self.reset()
            self.control_panel.auto_btn.config(text="⏸  일시정지")
            self._auto_batch()

    def _auto_batch(self):
        """Auto 모드: 속도에 따라 여러 스텝을 한 프레임에 묶어 처리.

        speed² 스텝을 한 번에 계산한 뒤 캔버스를 1회 갱신해
        대용량(128×128) 이미지에서도 부드럽게 재생된다.
        """
        if self._step_idx >= self.TOTAL_STEPS:
            self._auto_id = None
            self.control_panel.auto_btn.config(text="▶  Auto")
            return

        speed            = self.control_panel.speed_var.get()
        steps_per_frame  = speed * speed          # 1 ~ 100
        delay            = max(16, 500 // speed)  # 50 ~ 500 ms

        # 배치 내에서 공통으로 쓰는 입력 값을 한 번만 조회
        pixels = self.input_panel.get_pixels()
        fname  = self.control_panel.filter_var.get()
        kernel = FILTERS[fname]["kernel"]
        mode   = FILTERS[fname]["mode"]

        last_result = None
        last_row = last_col = 0

        for _ in range(steps_per_frame):
            if self._step_idx >= self.TOTAL_STEPS:
                break
            row, col = divmod(self._step_idx, OUT_N)
            result   = compute_one(pixels, kernel, row, col, mode)
            self._feature_map[row][col] = result["output_val"]
            self.output_panel.put_value(row, col, result["output_val"])  # 버퍼만 업데이트
            last_result = result
            last_row, last_col = row, col
            self._step_idx += 1

        # 배치 처리 후 캔버스 1회 갱신
        self.output_panel.refresh()
        self.input_panel.highlight(last_row, last_col)
        self.output_panel.highlight(last_row, last_col)
        self.control_panel.update_calc_display(last_result, last_row, last_col, mode)
        self.control_panel.update_progress(self._step_idx)

        if self._step_idx >= self.TOTAL_STEPS:
            self.input_panel.clear_highlight()
            self.output_panel.clear_highlight()
            self._auto_id = None
            self.control_panel.auto_btn.config(text="▶  Auto")
        else:
            self._auto_id = self.after(delay, self._auto_batch)

    def _cancel_auto(self):
        if self._auto_id is not None:
            self.after_cancel(self._auto_id)
            self._auto_id = None

    def reset(self):
        """전체 초기화."""
        self._cancel_auto()
        self._step_idx    = 0
        self._feature_map = [[None] * OUT_N for _ in range(OUT_N)]

        self.input_panel.clear_highlight()
        self.output_panel.clear()
        self.control_panel.update_progress(0)
        self.control_panel.show_idle()
        self.control_panel.auto_btn.config(text="▶  Auto")
