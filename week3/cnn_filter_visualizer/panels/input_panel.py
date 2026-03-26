import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from utils.image_loader import load_image_as_grid, DEFAULT_PIXELS, IMG_N

# 표시 캔버스 크기 (픽셀 단위)
IMG_DISPLAY = 256
IMG_PIXEL   = IMG_DISPLAY // IMG_N   # 셀당 화면 픽셀 수 (=2)

HL_COLOR    = "#FF4444"   # 슬라이딩 창 하이라이트 색


class InputPanel(tk.Frame):
    def __init__(self, parent, on_change_callback):
        super().__init__(parent, bg="#FFFFFF", padx=12, pady=12)
        self._on_change = on_change_callback
        self._pixels    = [row[:] for row in DEFAULT_PIXELS]
        self._hl_item   = None
        self._photo     = None   # PhotoImage 참조 유지 (GC 방지)

        self._build_title()
        self._build_canvas()
        self._build_upload_btn()
        self._redraw_image()

    def _build_title(self):
        tk.Label(
            self, text=f"입력 이미지 ({IMG_N}×{IMG_N})",
            font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#1A56A0"
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            self, text="이미지 파일을 불러오거나 기본 패턴 사용",
            font=("Arial", 9), bg="#FFFFFF", fg="#888888"
        ).pack(anchor="w", pady=(0, 6))

    def _build_canvas(self):
        self._canvas = tk.Canvas(
            self,
            width=IMG_DISPLAY, height=IMG_DISPLAY,
            bg="#CCCCCC",
            highlightthickness=1,
            highlightbackground="#CCCCCC",
            cursor="crosshair",
        )
        self._canvas.pack(pady=(0, 8))

    def _build_upload_btn(self):
        tk.Button(
            self,
            text="이미지 파일 열기  ↑",
            font=("Arial", 10),
            bg="#E6F1FB", fg="#1A56A0",
            activebackground="#B5D4F4",
            relief="flat", bd=0,
            padx=10, pady=6,
            cursor="hand2",
            command=self._upload,
        ).pack(fill="x")

        tk.Label(
            self, text=f"PNG / JPG / BMP  →  자동 {IMG_N}×{IMG_N} 변환",
            font=("Arial", 8), bg="#FFFFFF", fg="#AAAAAA"
        ).pack(pady=(3, 0))

    # ── 공개 API ──────────────────────────────────────────────────

    def get_pixels(self):
        """현재 픽셀 배열 복사본 반환 (IMG_N×IMG_N int list)."""
        return [row[:] for row in self._pixels]

    def set_pixels(self, pixels):
        """IMG_N×IMG_N int 배열을 내부에 저장하고 캔버스 갱신."""
        self._pixels = [row[:] for row in pixels]
        self.clear_highlight()
        self._redraw_image()

    def highlight(self, row, col):
        """(row, col) 기준 3×3 슬라이딩 창을 빨간 테두리 사각형으로 표시."""
        self.clear_highlight()
        x0 = col * IMG_PIXEL
        y0 = row * IMG_PIXEL
        x1 = (col + 3) * IMG_PIXEL
        y1 = (row + 3) * IMG_PIXEL
        self._hl_item = self._canvas.create_rectangle(
            x0, y0, x1, y1,
            outline=HL_COLOR, width=2, fill="",
        )

    def clear_highlight(self):
        if self._hl_item is not None:
            self._canvas.delete(self._hl_item)
            self._hl_item = None

    # ── 내부 ──────────────────────────────────────────────────────

    def _redraw_image(self):
        """PIL로 픽셀 배열을 이미지로 변환해 캔버스에 렌더링."""
        flat = bytes(
            self._pixels[r][c]
            for r in range(IMG_N)
            for c in range(IMG_N)
        )
        img = Image.frombytes("L", (IMG_N, IMG_N), flat)
        img = img.resize((IMG_DISPLAY, IMG_DISPLAY), Image.NEAREST)
        self._photo = ImageTk.PhotoImage(img)
        self._canvas.delete("img")
        self._canvas.create_image(0, 0, anchor="nw", image=self._photo, tags="img")

    def _upload(self):
        filepath = filedialog.askopenfilename(
            title="이미지 파일 선택",
            filetypes=[("이미지 파일", "*.png *.jpg *.jpeg *.bmp"), ("모든 파일", "*.*")],
        )
        if not filepath:
            return
        try:
            pixels = load_image_as_grid(filepath)
            self.set_pixels(pixels)
            self._on_change()
        except ImportError as e:
            messagebox.showerror("Pillow 없음", str(e))
        except Exception as e:
            messagebox.showerror("파일 오류", f"이미지를 불러올 수 없습니다.\n{e}")
