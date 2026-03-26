from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PySide6.QtCore import Qt
from PIL import Image
from utils.image_loader import IMG_N

OUT_N       = IMG_N - 2           # 126  (valid convolution 출력 크기)
OUT_DISPLAY = OUT_N * 2           # 252  (캔버스 표시 크기)
OUT_PIXEL   = OUT_DISPLAY // OUT_N  # = 2

EMPTY_GRAY  = 200
HL_COLOR    = "#3399FF"


def _pil_gray_to_qpixmap(pil_img):
    data  = pil_img.tobytes()
    qimg  = QImage(data, pil_img.width, pil_img.height,
                   pil_img.width, QImage.Format.Format_Grayscale8)
    return QPixmap.fromImage(qimg)


class _FeatureMapCanvas(QLabel):
    """Feature Map 이미지를 표시하고 하이라이트를 오버레이하는 QLabel 서브클래스."""

    def __init__(self):
        super().__init__()
        self._hl_rect = None
        self.setFixedSize(OUT_DISPLAY, OUT_DISPLAY)
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


class OutputPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._out_img = Image.new("L", (OUT_N, OUT_N), EMPTY_GRAY)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel(f"출력 Feature Map ({OUT_N}×{OUT_N})")
        title.setStyleSheet("font-size:12px; font-weight:bold; color:#0F6E56;")
        layout.addWidget(title)

        subtitle = QLabel("밝은 픽셀: 높은 활성화 / 어두운 픽셀: 낮은 활성화")
        subtitle.setStyleSheet("font-size:9px; color:#888888;")
        layout.addWidget(subtitle)

        self._canvas = _FeatureMapCanvas()
        layout.addWidget(self._canvas)

        self._update_canvas()

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
        x0 = col * OUT_PIXEL
        y0 = row * OUT_PIXEL
        x1 = x0 + OUT_PIXEL
        y1 = y0 + OUT_PIXEL
        self._canvas.set_highlight(x0, y0, x1, y1)

    def clear_highlight(self):
        self._canvas.clear_highlight()

    def clear(self):
        self._out_img = Image.new("L", (OUT_N, OUT_N), EMPTY_GRAY)
        self.clear_highlight()
        self._update_canvas()

    # ── 내부 ──────────────────────────────────────────────────────

    def _update_canvas(self):
        scaled = self._out_img.resize((OUT_DISPLAY, OUT_DISPLAY), Image.NEAREST)
        self._canvas.setPixmap(_pil_gray_to_qpixmap(scaled))
