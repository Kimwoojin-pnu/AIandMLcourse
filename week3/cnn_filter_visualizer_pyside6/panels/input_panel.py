from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                                QFileDialog, QMessageBox)
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PySide6.QtCore import Qt
from PIL import Image
from utils.image_loader import load_image_as_grid, DEFAULT_PIXELS, IMG_N

IMG_DISPLAY = 256
IMG_PIXEL   = IMG_DISPLAY // IMG_N   # 셀당 화면 픽셀 수 (= 2)
HL_COLOR    = "#FF4444"


def _pil_gray_to_qpixmap(pil_img):
    """그레이스케일 PIL 이미지 → QPixmap 변환."""
    data  = pil_img.tobytes()
    qimg  = QImage(data, pil_img.width, pil_img.height,
                   pil_img.width, QImage.Format.Format_Grayscale8)
    return QPixmap.fromImage(qimg)


class _ImageCanvas(QLabel):
    """이미지를 표시하고 하이라이트 사각형을 오버레이하는 QLabel 서브클래스."""

    def __init__(self):
        super().__init__()
        self._hl_rect = None   # (x0, y0, x1, y1) 디스플레이 픽셀 기준
        self.setFixedSize(IMG_DISPLAY, IMG_DISPLAY)
        self.setStyleSheet("border:1px solid #CCCCCC;")

    def set_highlight(self, x0, y0, x1, y1):
        self._hl_rect = (x0, y0, x1, y1)
        self.update()

    def clear_highlight(self):
        self._hl_rect = None
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._hl_rect:
            painter = QPainter(self)
            pen = QPen(QColor(HL_COLOR))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            x0, y0, x1, y1 = self._hl_rect
            painter.drawRect(x0, y0, x1 - x0, y1 - y0)
            painter.end()


class InputPanel(QWidget):
    def __init__(self, on_change_callback):
        super().__init__()
        self._on_change = on_change_callback
        self._pixels    = [row[:] for row in DEFAULT_PIXELS]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 타이틀
        title = QLabel(f"입력 이미지 ({IMG_N}×{IMG_N})")
        title.setStyleSheet("font-size:12px; font-weight:bold; color:#1A56A0;")
        layout.addWidget(title)

        subtitle = QLabel("이미지 파일을 불러오거나 기본 패턴 사용")
        subtitle.setStyleSheet("font-size:9px; color:#888888;")
        layout.addWidget(subtitle)

        # 이미지 캔버스
        self._canvas = _ImageCanvas()
        layout.addWidget(self._canvas)

        # 업로드 버튼
        upload_btn = QPushButton("이미지 파일 열기  ↑")
        upload_btn.setStyleSheet(
            "QPushButton { background:#E6F1FB; color:#1A56A0; border:none;"
            " padding:6px 10px; font-size:10px; }"
            "QPushButton:hover { background:#B5D4F4; }"
        )
        upload_btn.clicked.connect(self._upload)
        layout.addWidget(upload_btn)

        hint = QLabel(f"PNG / JPG / BMP  →  자동 {IMG_N}×{IMG_N} 변환")
        hint.setStyleSheet("font-size:8px; color:#AAAAAA;")
        layout.addWidget(hint)

        self._redraw_image()

    # ── 공개 API ──────────────────────────────────────────────────

    def get_pixels(self):
        return [row[:] for row in self._pixels]

    def set_pixels(self, pixels):
        self._pixels = [row[:] for row in pixels]
        self.clear_highlight()
        self._redraw_image()

    def highlight(self, row, col):
        x0 = col * IMG_PIXEL
        y0 = row * IMG_PIXEL
        x1 = (col + 3) * IMG_PIXEL
        y1 = (row + 3) * IMG_PIXEL
        self._canvas.set_highlight(x0, y0, x1, y1)

    def clear_highlight(self):
        self._canvas.clear_highlight()

    # ── 내부 ──────────────────────────────────────────────────────

    def _redraw_image(self):
        flat = bytes(self._pixels[r][c] for r in range(IMG_N) for c in range(IMG_N))
        img  = Image.frombytes("L", (IMG_N, IMG_N), flat)
        img  = img.resize((IMG_DISPLAY, IMG_DISPLAY), Image.NEAREST)
        self._canvas.setPixmap(_pil_gray_to_qpixmap(img))

    def _upload(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "이미지 파일 선택", "",
            "이미지 파일 (*.png *.jpg *.jpeg *.bmp);;모든 파일 (*.*)",
        )
        if not filepath:
            return
        try:
            pixels = load_image_as_grid(filepath)
            self.set_pixels(pixels)
            self._on_change()
        except ImportError as e:
            QMessageBox.critical(self, "Pillow 없음", str(e))
        except Exception as e:
            QMessageBox.critical(self, "파일 오류", f"이미지를 불러올 수 없습니다.\n{e}")
