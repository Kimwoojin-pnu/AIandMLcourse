import tkinter as tk
from logic.filters import FILTERS, FILTER_NAMES

K_POS_BG  = "#E6F1FB"
K_NEG_BG  = "#FAECE7"
K_ZER_BG  = "#F0F0F0"
K_POS_FG  = "#0C447C"
K_NEG_FG  = "#712B13"
K_ZER_FG  = "#888888"

PATCH_BG  = "#E6F1FB"
PROD_POS  = "#E2F0EB"
PROD_NEG  = "#FAECE7"
PROD_ZER  = "#F4F4F4"


class ControlPanel(tk.Frame):
    def __init__(self, parent, app, total_steps):
        super().__init__(parent, bg="#FFFFFF", padx=14, pady=12)
        self._app         = app
        self._total_steps = total_steps
        self.filter_var   = tk.StringVar(value=FILTER_NAMES[0])
        self.speed_var    = tk.IntVar(value=4)

        self._build_filter_section()
        self._separator()
        self._build_kernel_display()
        self._separator()
        self._build_calc_display()
        self._separator()
        self._build_buttons()
        self._build_speed_slider()
        self._separator()
        self._build_progress()

        self.update_kernel_display(FILTER_NAMES[0])
        self.show_idle()

    # ── 필터 선택 ──────────────────────────────────────────────

    def _build_filter_section(self):
        tk.Label(
            self, text="필터 선택",
            font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#1A56A0"
        ).pack(anchor="w", pady=(0, 6))

        for name in FILTER_NAMES:
            row = tk.Frame(self, bg="#FFFFFF")
            row.pack(anchor="w", pady=1)
            tk.Radiobutton(
                row,
                text=name,
                variable=self.filter_var,
                value=name,
                font=("Arial", 11),
                bg="#FFFFFF",
                activebackground="#FFFFFF",
                fg="#222222",
                selectcolor="#DEEAF1",
                command=self._on_filter_change,
            ).pack(side="left")
            desc = FILTERS[name]["desc"]
            tk.Label(
                row, text=f"  ({desc})",
                font=("Arial", 8), bg="#FFFFFF", fg="#999999"
            ).pack(side="left")

    def _on_filter_change(self):
        self.update_kernel_display(self.filter_var.get())
        self._app.on_filter_change()

    # ── 커널 표시 ─────────────────────────────────────────────

    def _build_kernel_display(self):
        tk.Label(
            self, text="커널 (3×3)",
            font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#333333"
        ).pack(anchor="w", pady=(0, 4))

        self._kernel_frame = tk.Frame(self, bg="#FFFFFF")
        self._kernel_frame.pack(anchor="w")

        self._kernel_labels = [[None] * 3 for _ in range(3)]
        for r in range(3):
            for c in range(3):
                lbl = tk.Label(
                    self._kernel_frame,
                    text="0",
                    width=3,
                    font=("Courier New", 12, "bold"),
                    relief="flat",
                    pady=6,
                    padx=4,
                )
                lbl.grid(row=r, column=c, padx=2, pady=2)
                self._kernel_labels[r][c] = lbl

    def update_kernel_display(self, filter_name):
        kernel = FILTERS[filter_name]["kernel"]
        for r in range(3):
            for c in range(3):
                v = kernel[r][c]
                if v > 0:
                    bg, fg = K_POS_BG, K_POS_FG
                elif v < 0:
                    bg, fg = K_NEG_BG, K_NEG_FG
                else:
                    bg, fg = K_ZER_BG, K_ZER_FG
                self._kernel_labels[r][c].config(text=str(v), bg=bg, fg=fg)

    # ── 계산식 표시 ───────────────────────────────────────────

    def _build_calc_display(self):
        tk.Label(
            self, text="계산 과정 (현재 위치)",
            font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#333333"
        ).pack(anchor="w", pady=(0, 4))

        self._pos_lbl = tk.Label(
            self, text="",
            font=("Arial", 9), bg="#FFFFFF", fg="#555555"
        )
        self._pos_lbl.pack(anchor="w")

        self._math_frame = tk.Frame(self, bg="#FFFFFF")
        self._math_frame.pack(anchor="w", pady=4)

        self._patch_lbls = self._make_3x3_grid(self._math_frame, col_offset=0)
        tk.Label(self._math_frame, text="×", font=("Arial", 18),
                 bg="#FFFFFF", fg="#AAAAAA").grid(row=1, column=3, padx=4)
        self._kcopy_lbls = self._make_3x3_grid(self._math_frame, col_offset=4)
        tk.Label(self._math_frame, text="=", font=("Arial", 18),
                 bg="#FFFFFF", fg="#AAAAAA").grid(row=1, column=7, padx=4)
        self._prod_lbls  = self._make_3x3_grid(self._math_frame, col_offset=8)

        self._sum_lbl = tk.Label(
            self, text="",
            font=("Arial", 10), bg="#FFFFFF", fg="#333333",
            wraplength=260, justify="left"
        )
        self._sum_lbl.pack(anchor="w", pady=(6, 0))

        self._out_lbl = tk.Label(
            self, text="",
            font=("Arial", 14, "bold"), bg="#FFFFFF", fg="#0F6E56"
        )
        self._out_lbl.pack(anchor="w", pady=(2, 0))

    def _make_3x3_grid(self, parent, col_offset):
        lbls = []
        for i in range(9):
            r, c = divmod(i, 3)
            lbl = tk.Label(
                parent, text="", width=4,
                font=("Courier New", 9),
                bg="#F0F0F0", fg="#333333",
                relief="flat", padx=2, pady=3,
            )
            lbl.grid(row=r, column=c + col_offset, padx=1, pady=1)
            lbls.append(lbl)
        return lbls

    def update_calc_display(self, result, row, col, mode):
        self._pos_lbl.config(
            text=f"위치  행 {row},  열 {col}  →  Feature Map [{row}][{col}]"
        )

        for i, v in enumerate(result["patch"]):
            self._patch_lbls[i].config(text=str(v), bg=PATCH_BG, fg="#0C447C")

        kflat = result["kflat"]
        for i, v in enumerate(kflat):
            if v > 0:   bg, fg = K_POS_BG, K_POS_FG
            elif v < 0: bg, fg = K_NEG_BG, K_NEG_FG
            else:       bg, fg = K_ZER_BG, K_ZER_FG
            self._kcopy_lbls[i].config(text=str(v), bg=bg, fg=fg)

        for i, v in enumerate(result["products"]):
            if v > 0:   bg, fg = PROD_POS, "#085041"
            elif v < 0: bg, fg = PROD_NEG, "#712B13"
            else:       bg, fg = PROD_ZER, "#888888"
            self._prod_lbls[i].config(text=str(v), bg=bg, fg=fg)

        raw  = result["raw_sum"]
        oval = result["output_val"]
        if mode == "abs":
            process = f"|{raw}| = {abs(raw)}  →  clamp(0,255) = {oval}"
        else:
            process = f"clamp(0, 255, {raw}) = {oval}"

        self._sum_lbl.config(text=f"모두 더하면: {raw}    {process}")
        color = "#0F6E56" if oval > 180 else ("#1A56A0" if oval > 50 else "#993C1D")
        self._out_lbl.config(text=f"출력값  →  {oval}", fg=color)

    def show_idle(self):
        self._pos_lbl.config(text="Step 버튼을 눌러 시작하세요.")
        for lbl in self._patch_lbls + self._kcopy_lbls + self._prod_lbls:
            lbl.config(text="", bg="#F0F0F0", fg="#333333")
        self._sum_lbl.config(text="")
        self._out_lbl.config(text="")

    # ── 버튼 ─────────────────────────────────────────────────

    def _build_buttons(self):
        frame = tk.Frame(self, bg="#FFFFFF")
        frame.pack(anchor="w", pady=(2, 0))

        btn_cfg = dict(font=("Arial", 11), relief="flat", bd=0,
                       padx=12, pady=7, cursor="hand2")

        tk.Button(frame, text="↺  Reset",
                  bg="#F0F0F0", fg="#444444",
                  activebackground="#DDDDDD",
                  command=self._app.reset,
                  **btn_cfg).grid(row=0, column=0, padx=(0, 6))

        tk.Button(frame, text="Step  →",
                  bg="#DEEAF1", fg="#1A56A0",
                  activebackground="#B5D4F4",
                  command=self._app.step,
                  **btn_cfg).grid(row=0, column=1, padx=(0, 6))

        self.auto_btn = tk.Button(
            frame, text="▶  Auto",
            bg="#E2F0EB", fg="#085041",
            activebackground="#9FE1CB",
            command=self._app.toggle_auto,
            **btn_cfg
        )
        self.auto_btn.grid(row=0, column=2)

    def _build_speed_slider(self):
        row = tk.Frame(self, bg="#FFFFFF")
        row.pack(anchor="w", pady=(8, 0))

        tk.Label(row, text="속도", font=("Arial", 10),
                 bg="#FFFFFF", fg="#555555").pack(side="left")
        tk.Scale(row,
                 variable=self.speed_var,
                 from_=1, to=10, orient="horizontal",
                 length=160, showvalue=True,
                 bg="#FFFFFF", troughcolor="#E0E0E0",
                 highlightthickness=0,
                 font=("Arial", 9),
                 command=lambda _: self._app.on_speed_change(),
                 ).pack(side="left", padx=8)
        tk.Label(row, text="느림 ← → 빠름",
                 font=("Arial", 8), bg="#FFFFFF", fg="#AAAAAA").pack(side="left")

    # ── 진행 표시 ─────────────────────────────────────────────

    def _build_progress(self):
        self._progress_lbl = tk.Label(
            self, text=f"0 / {self._total_steps:,}",
            font=("Arial", 10), bg="#FFFFFF", fg="#888888"
        )
        self._progress_lbl.pack(anchor="w")

    def update_progress(self, step_idx):
        self._progress_lbl.config(
            text=f"{step_idx:,} / {self._total_steps:,}",
            fg="#888888"
        )
        if step_idx >= self._total_steps:
            self._progress_lbl.config(
                text="완료! 다른 필터로 바꿔보세요.",
                fg="#0F6E56"
            )

    # ── 유틸 ──────────────────────────────────────────────────

    def _separator(self):
        tk.Frame(self, height=1, bg="#EEEEEE").pack(fill="x", pady=8)
