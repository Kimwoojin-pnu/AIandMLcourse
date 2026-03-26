import tkinter as tk
from PIL import Image, ImageTk
from utils.image_loader import IMG_N

OUT_N       = IMG_N - 2          # 126 (valid convolution 출력 크기)
OUT_DISPLAY = OUT_N * 2          # 252 (캔버스 표시 크기)
OUT_PIXEL   = OUT_DISPLAY // OUT_N  # = 2

EMPTY_GRAY  = 200   # 미완료 셀 회색값
HL_COLOR    = "#3399FF"


class OutputPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#FFFFFF", padx=12, pady=12)
        self._hl_item   = None
        self._img_id    = None
        # PIL 이미지 버퍼: 완료 픽셀은 실제 값, 미완료는 EMPTY_GRAY
        self._out_img   = Image.new("L", (OUT_N, OUT_N), EMPTY_GRAY)
        self._out_photo = None

        self._build_title()
        self._build_canvas()
        self._update_canvas()

    def _build_title(self):
        tk.Label(
            self, text=f"출력 Feature Map ({OUT_N}×{OUT_N})",
            font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#0F6E56"
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            self, text="밝은 픽셀: 높은 활성화 / 어두운 픽셀: 낮은 활성화",
            font=("Arial", 9), bg="#FFFFFF", fg="#888888"
        ).pack(anchor="w", pady=(0, 6))

    def _build_canvas(self):
        self._canvas = tk.Canvas(
            self,
            width=OUT_DISPLAY, height=OUT_DISPLAY,
            bg="#CCCCCC",
            highlightthickness=1,
            highlightbackground="#CCCCCC",
        )
        self._canvas.pack()

    # ── 공개 API ──────────────────────────────────────────────────

    def set_value(self, row, col, value):
        """Feature Map 한 셀 업데이트 + 즉시 캔버스 갱신 (수동 Step용)."""
        self._out_img.putpixel((col, row), int(value))
        self._update_canvas()

    def put_value(self, row, col, value):
        """Feature Map 한 셀 업데이트만 (캔버스 갱신 없음, Auto 배치용)."""
        self._out_img.putpixel((col, row), int(value))

    def refresh(self):
        """PIL 버퍼를 캔버스에 반영 (Auto 배치 후 1회 호출)."""
        self._update_canvas()

    def highlight(self, row, col):
        """현재 처리 위치를 파란 테두리로 표시."""
        if self._hl_item is not None:
            self._canvas.delete(self._hl_item)
        x0 = col * OUT_PIXEL
        y0 = row * OUT_PIXEL
        x1 = x0 + OUT_PIXEL
        y1 = y0 + OUT_PIXEL
        self._hl_item = self._canvas.create_rectangle(
            x0, y0, x1, y1,
            outline=HL_COLOR, width=2, fill="",
        )

    def clear_highlight(self):
        if self._hl_item is not None:
            self._canvas.delete(self._hl_item)
            self._hl_item = None

    def clear(self):
        """Feature Map 초기화 (회색으로 리셋)."""
        self._out_img = Image.new("L", (OUT_N, OUT_N), EMPTY_GRAY)
        self.clear_highlight()
        self._update_canvas()

    # ── 내부 ──────────────────────────────────────────────────────

    def _update_canvas(self):
        """PIL 버퍼를 NEAREST 스케일링해 캔버스에 그린다."""
        scaled          = self._out_img.resize((OUT_DISPLAY, OUT_DISPLAY), Image.NEAREST)
        self._out_photo = ImageTk.PhotoImage(scaled)
        if self._img_id is None:
            self._img_id = self._canvas.create_image(
                0, 0, anchor="nw", image=self._out_photo, tags="fmap"
            )
        else:
            self._canvas.itemconfig(self._img_id, image=self._out_photo)
