import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import ast
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QPushButton, QProgressBar,
    QLineEdit, QComboBox, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from .colors import COLORS
from .train_worker import TrainWorker
from .matplotlib_canvas import MatplotlibCanvas
from .nn_diagram import NNDiagramWidget


# ── Typography helpers ──────────────────────────────────────────────────────

def _mono_font(size: int = 10) -> QFont:
    f = QFont("Consolas")
    if not f.exactMatch():
        f = QFont("Courier New")
    f.setPointSize(size)
    return f


def _label_qss(color: str, size: int = 9, bold: bool = False) -> str:
    w = "600" if bold else "400"
    return (
        f"color: {color}; font-size: {size}pt; font-weight: {w}; "
        f"background: transparent; border: none; font-family: Consolas, 'Courier New', monospace;"
    )


# ── QSS constants ───────────────────────────────────────────────────────────

_INPUT_QSS = f"""
    QLineEdit {{
        background: {COLORS['bg']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border_light']};
        border-radius: 0px;
        padding: 4px 8px;
        font-size: 9pt;
        font-family: Consolas, 'Courier New', monospace;
        selection-background-color: {COLORS['accent']};
    }}
    QLineEdit:focus {{
        border: 1px solid {COLORS['accent']};
    }}
"""

_COMBO_QSS = f"""
    QComboBox {{
        background: {COLORS['bg']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border_light']};
        border-radius: 0px;
        padding: 4px 8px;
        font-size: 9pt;
        font-family: Consolas, 'Courier New', monospace;
    }}
    QComboBox::drop-down {{ border: none; }}
    QComboBox::down-arrow {{
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {COLORS['accent']};
        margin-right: 6px;
    }}
    QComboBox QAbstractItemView {{
        background: {COLORS['card']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border_light']};
        selection-background-color: {COLORS['accent']};
        selection-color: {COLORS['bg']};
        font-family: Consolas, 'Courier New', monospace;
    }}
"""

_SLIDER_QSS = f"""
    QSlider::groove:horizontal {{
        height: 3px;
        background: {COLORS['border_light']};
        border-radius: 0px;
    }}
    QSlider::handle:horizontal {{
        background: {COLORS['accent']};
        width: 10px;
        height: 10px;
        margin: -4px 0;
        border-radius: 0px;
    }}
    QSlider::sub-page:horizontal {{
        background: {COLORS['accent']};
    }}
"""


def _make_btn(label: str, bg: str, fg: str = None) -> QPushButton:
    fg = fg or COLORS["bg"]
    btn = QPushButton(label)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {bg};
            color: {fg};
            border: none;
            border-radius: 0px;
            padding: 7px 10px;
            font-size: 8pt;
            font-weight: 700;
            font-family: Consolas, 'Courier New', monospace;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        QPushButton:hover {{
            background: {COLORS['text']};
            color: {COLORS['bg']};
        }}
        QPushButton:disabled {{
            background: {COLORS['border']};
            color: {COLORS['text_muted']};
        }}
    """)
    return btn


def _make_sep(layout) -> None:
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    sep.setStyleSheet(
        f"background: {COLORS['border']}; max-height: 1px; border: none;"
    )
    layout.addWidget(sep)


# ── BaseLabWindow ───────────────────────────────────────────────────────────

class BaseLabWindow(QMainWindow):
    DEFAULT_PARAMS = {
        "layers": "[64, 64]",
        "activation": "relu",
        "epochs": 500,
        "lr": 0.001,
    }

    def __init__(self, title: str, footer_text: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(1120, 700)
        self._worker: TrainWorker | None = None
        self._current_model = None
        self._total_epochs = self.DEFAULT_PARAMS["epochs"]
        self._loss_history: dict = {"loss": [], "val_loss": []}
        self._build_ui(title, footer_text)
        QTimer.singleShot(300, self._on_train_clicked)

    # ── Build UI ────────────────────────────────────────────────────────

    def _build_ui(self, title: str, footer_text: str):
        bg = COLORS["bg"]
        self.setStyleSheet(f"QMainWindow, QWidget#central {{ background: {bg}; }}")
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        root.addWidget(self._make_header(title))

        body = QWidget()
        body.setStyleSheet(f"background: {bg};")
        hbox = QHBoxLayout(body)
        hbox.setContentsMargins(12, 10, 12, 10)
        hbox.setSpacing(8)
        root.addWidget(body, stretch=1)

        hbox.addWidget(self._make_left_panel())

        center_frame = QFrame()
        center_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['panel']};
                border: 1px solid {COLORS['border']};
            }}
        """)
        cl = QVBoxLayout(center_frame)
        cl.setContentsMargins(6, 6, 6, 6)
        self.main_canvas = self._build_main_chart()
        cl.addWidget(self.main_canvas)
        hbox.addWidget(center_frame, stretch=1)
        hbox.addWidget(self._make_right_panel())

        root.addWidget(self._make_status_bar(footer_text))

    def _make_header(self, title: str) -> QWidget:
        w = QWidget()
        w.setFixedHeight(48)
        w.setStyleSheet(
            f"background: {COLORS['panel']};"
            f"border-bottom: 2px solid {COLORS['accent']};"
        )
        h = QHBoxLayout(w)
        h.setContentsMargins(18, 0, 18, 0)

        lbl = QLabel(title.upper())
        lbl.setStyleSheet(
            f"color: {COLORS['accent']}; font-size: 11pt; font-weight: 700; "
            f"font-family: Consolas, 'Courier New', monospace; "
            f"letter-spacing: 2px; background: transparent;"
        )
        h.addWidget(lbl)
        h.addStretch()

        sub = QLabel("MIT 6.S191  ·  WEEK 4  ·  NEURAL NETWORK VISUALIZER")
        sub.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 7pt; "
            f"font-family: Consolas, 'Courier New', monospace; "
            f"letter-spacing: 1px; background: transparent;"
        )
        h.addWidget(sub)
        return w

    def _make_status_bar(self, text: str) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(36)
        bar.setStyleSheet(
            f"background: {COLORS['panel']}; "
            f"border-top: 1px solid {COLORS['border']};"
        )
        h = QHBoxLayout(bar)
        h.setContentsMargins(12, 0, 12, 0)
        h.setSpacing(12)

        self._epoch_bar = QProgressBar()
        self._epoch_bar.setRange(0, 100)
        self._epoch_bar.setValue(0)
        self._epoch_bar.setTextVisible(False)
        self._epoch_bar.setFixedHeight(10)
        self._epoch_bar.setFixedWidth(220)
        self._epoch_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {COLORS['border']};
                border: none;
                border-radius: 0px;
            }}
            QProgressBar::chunk {{
                background: {COLORS['success']};
            }}
        """)
        h.addWidget(self._epoch_bar)

        self._epoch_label = QLabel("READY")
        self._epoch_label.setStyleSheet(_label_qss(COLORS["text_muted"], 8))
        h.addWidget(self._epoch_label)
        h.addStretch()

        footer_lbl = QLabel(text.upper() if text else "PYSIDE6 · TENSORFLOW/KERAS · MATPLOTLIB")
        footer_lbl.setStyleSheet(_label_qss(COLORS["text_muted"], 7))
        h.addWidget(footer_lbl)
        return bar

    # ── Left Panel ───────────────────────────────────────────────────────

    def _make_left_panel(self) -> QFrame:
        card = self._make_panel_card()
        card.setFixedWidth(220)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(5)

        self._add_section_label(layout, "PARAMETERS")

        for field_label, attr_name, key in [
            ("Hidden Layers", "_inp_hidden_layers", "layers"),
            ("Epochs",        "_inp_epochs",        "epochs"),
            ("Learning Rate", "_inp_learning_rate", "lr"),
        ]:
            self._add_field_label(layout, field_label)
            inp = QLineEdit(str(self.DEFAULT_PARAMS[key]))
            inp.setStyleSheet(_INPUT_QSS)
            layout.addWidget(inp)
            setattr(self, attr_name, inp)

        self._add_field_label(layout, "Activation")
        self._inp_activation = QComboBox()
        self._inp_activation.addItems(["relu", "tanh", "sigmoid", "elu"])
        self._inp_activation.setCurrentText(str(self.DEFAULT_PARAMS["activation"]))
        self._inp_activation.setStyleSheet(_COMBO_QSS)
        layout.addWidget(self._inp_activation)

        custom = self._build_custom_controls()
        if custom is not None:
            _make_sep(layout)
            layout.addWidget(custom)

        layout.addStretch()
        _make_sep(layout)

        btn_train = _make_btn("▶  TRAIN", COLORS["accent"])
        btn_stop  = _make_btn("■  STOP",  COLORS["danger"])
        btn_reset = _make_btn("↺  RESET", COLORS["border"], COLORS["text_dim"])
        layout.addWidget(btn_train)
        layout.addWidget(btn_stop)
        layout.addWidget(btn_reset)

        self._btn_train = btn_train
        self._btn_stop  = btn_stop
        self._btn_reset = btn_reset
        self._btn_train.clicked.connect(self._on_train_clicked)
        self._btn_stop.clicked.connect(self._on_stop_clicked)
        self._btn_reset.clicked.connect(self._on_reset_clicked)
        self._btn_stop.setEnabled(False)

        return card

    # ── Right Panel ──────────────────────────────────────────────────────

    def _make_right_panel(self) -> QFrame:
        card = self._make_panel_card()
        card.setFixedWidth(190)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(5)

        self._add_section_label(layout, "TRAINING")
        self._stat_labels: dict[str, QLabel] = {}
        for key, color in [
            ("Train Loss", COLORS["danger"]),
            ("Val Loss",   COLORS["info"]),
            ("MAE",        COLORS["success"]),
        ]:
            self._add_field_label(layout, key)
            v = QLabel("—")
            v.setStyleSheet(_label_qss(color, 11, bold=True))
            layout.addWidget(v)
            self._stat_labels[key] = v

        self.loss_canvas = MatplotlibCanvas(nrows=1, ncols=1)
        self.loss_canvas.setFixedHeight(85)
        layout.addWidget(self.loss_canvas)

        _make_sep(layout)
        self._add_section_label(layout, "ARCHITECTURE")

        self._nn_diagram = NNDiagramWidget()
        self._nn_diagram.setFixedHeight(110)
        layout.addWidget(self._nn_diagram)

        custom_info = self._build_custom_info()
        if custom_info is not None:
            _make_sep(layout)
            layout.addWidget(custom_info)

        layout.addStretch()
        return card

    # ── Style helpers ────────────────────────────────────────────────────

    def _make_panel_card(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['panel']};
                border: 1px solid {COLORS['border']};
                border-left: 3px solid {COLORS['accent']};
            }}
        """)
        return f

    def _add_section_label(self, layout, text: str):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {COLORS['accent']}; font-size: 8pt; font-weight: 700; "
            f"letter-spacing: 2px; background: transparent; border: none; "
            f"font-family: Consolas, 'Courier New', monospace; "
            f"padding-bottom: 3px;"
        )
        layout.addWidget(lbl)

    def _add_field_label(self, layout, text: str):
        lbl = QLabel(text.upper())
        lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 7pt; "
            f"letter-spacing: 1px; background: transparent; border: none; "
            f"font-family: Consolas, 'Courier New', monospace;"
        )
        layout.addWidget(lbl)

    def _input_qss(self) -> str:
        return _INPUT_QSS

    def _combo_qss(self) -> str:
        return _COMBO_QSS

    def _slider_qss(self) -> str:
        return _SLIDER_QSS

    # ── Abstract interface ───────────────────────────────────────────────

    def _build_custom_controls(self) -> QWidget | None:
        return None

    def _build_main_chart(self) -> QWidget:
        raise NotImplementedError

    def _build_custom_info(self) -> QWidget | None:
        return None

    def _get_model_and_data(self) -> tuple:
        raise NotImplementedError

    def _on_train_complete(self, history):
        self._epoch_label.setText("DONE ✓")
        self._btn_train.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._nn_diagram.set_training(False)

    def _reset_custom(self):
        pass

    # ── NN diagram helper ────────────────────────────────────────────────

    def _update_nn_diagram(self):
        """Parse layer config and push to the diagram widget."""
        try:
            hidden = self._parse_layers()
        except Exception:
            hidden = []
        # Infer input/output from model if available, else generic 1/1
        in_size = 1
        out_size = 1
        if self._current_model is not None:
            try:
                in_size = self._current_model.input_shape[-1]
                out_size = self._current_model.output_shape[-1]
            except Exception:
                pass
        self._nn_diagram.set_layers([in_size] + hidden + [out_size])

    # ── Slots ────────────────────────────────────────────────────────────

    def _on_epoch_done(self, epoch: int, logs: dict):
        pct = int((epoch + 1) / self._total_epochs * 100)
        self._epoch_bar.setValue(pct)
        self._epoch_label.setText(f"EPOCH  {epoch + 1} / {self._total_epochs}")

        loss    = logs.get("loss", 0.0)
        val_loss = logs.get("val_loss", 0.0)
        mae      = logs.get("mae", logs.get("mean_absolute_error", 0.0))
        self._stat_labels["Train Loss"].setText(f"{loss:.5f}")
        self._stat_labels["Val Loss"].setText(f"{val_loss:.5f}")
        self._stat_labels["MAE"].setText(f"{mae:.4f}")

        self._loss_history["loss"].append(loss)
        self._loss_history["val_loss"].append(val_loss)

        ax = self.loss_canvas.ax
        ax.cla()
        ax.set_facecolor(COLORS["bg"])
        ax.plot(self._loss_history["loss"],     color=COLORS["danger"], linewidth=1)
        ax.plot(self._loss_history["val_loss"], color=COLORS["info"],   linewidth=1)
        ax.tick_params(labelsize=7, colors=COLORS["text_muted"])
        for sp in ax.spines.values():
            sp.set_edgecolor(COLORS["border"])
        self.loss_canvas.draw()

    def _on_train_clicked(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()

        self._loss_history = {"loss": [], "val_loss": []}
        self._epoch_bar.setValue(0)

        try:
            model, x_train, y_train = self._get_model_and_data()
        except Exception as exc:
            self._epoch_label.setText(f"ERROR: {exc}")
            return

        self._current_model = model
        self._total_epochs = int(self._inp_epochs.text())

        self._update_nn_diagram()
        self._nn_diagram.set_training(True)

        self._worker = TrainWorker(model, x_train, y_train,
                                   self._total_epochs, val_split=0.1)
        self._worker.epoch_done.connect(self._on_epoch_done)
        self._worker.train_done.connect(self._on_train_complete)
        self._worker.train_error.connect(
            lambda e: self._epoch_label.setText(f"ERROR: {e}")
        )
        self._worker.start()
        self._btn_train.setEnabled(False)
        self._btn_stop.setEnabled(True)
        self._epoch_label.setText("TRAINING…")

    def _on_stop_clicked(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
        self._btn_train.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._epoch_label.setText("STOPPED")
        self._nn_diagram.set_training(False)

    def _on_reset_clicked(self):
        self._on_stop_clicked()
        self._inp_hidden_layers.setText(str(self.DEFAULT_PARAMS["layers"]))
        self._inp_epochs.setText(str(self.DEFAULT_PARAMS["epochs"]))
        self._inp_learning_rate.setText(str(self.DEFAULT_PARAMS["lr"]))
        self._inp_activation.setCurrentText(str(self.DEFAULT_PARAMS["activation"]))
        for lbl in self._stat_labels.values():
            lbl.setText("—")
        self._epoch_bar.setValue(0)
        self._epoch_label.setText("READY")
        self._loss_history = {"loss": [], "val_loss": []}
        self.loss_canvas.clear()
        self.loss_canvas.draw()
        self._reset_custom()

    # ── Helpers ──────────────────────────────────────────────────────────

    def _parse_layers(self) -> list[int]:
        text = self._inp_hidden_layers.text().strip()
        result = ast.literal_eval(text)
        return [result] if isinstance(result, int) else list(result)

    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()
        super().closeEvent(event)
