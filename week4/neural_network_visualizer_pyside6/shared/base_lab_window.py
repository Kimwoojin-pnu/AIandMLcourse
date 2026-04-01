import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QPushButton, QProgressBar,
    QLineEdit, QComboBox, QGraphicsOpacityEffect,
)
from PySide6.QtCore import Qt, QTimer, QByteArray
from PySide6.QtSvgWidgets import QSvgWidget
from .colors import COLORS, CAT_SVG
from .train_worker import TrainWorker
from .matplotlib_canvas import MatplotlibCanvas


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
        self.setMinimumSize(1100, 680)
        self._worker: TrainWorker | None = None
        self._current_model = None
        self._total_epochs = self.DEFAULT_PARAMS["epochs"]
        self._loss_history: dict = {"loss": [], "val_loss": []}
        self._build_ui(title, footer_text)
        QTimer.singleShot(300, self._on_train_clicked)

    # ── UI Construction ──────────────────────────────────────────────

    def _build_ui(self, title: str, footer_text: str):
        self.setStyleSheet(f"QMainWindow, QWidget {{ background: {COLORS['bg']}; }}")
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        root.addWidget(self._make_header(title))

        body = QWidget()
        hbox = QHBoxLayout(body)
        hbox.setContentsMargins(12, 10, 12, 10)
        hbox.setSpacing(8)
        root.addWidget(body, stretch=1)

        hbox.addWidget(self._make_left_panel())
        center_card = self._make_card()
        cl = QVBoxLayout(center_card)
        cl.setContentsMargins(6, 6, 6, 6)
        self.main_canvas = self._build_main_chart()
        cl.addWidget(self.main_canvas)
        hbox.addWidget(center_card, stretch=1)
        hbox.addWidget(self._make_right_panel())

        root.addWidget(self._make_footer(footer_text))

    def _make_header(self, title: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {COLORS['panel']}; border-bottom: 1px solid {COLORS['border']};")
        h = QHBoxLayout(w)
        h.setContentsMargins(14, 8, 14, 8)
        lbl = QLabel(f"{title}  |  MIT 6.S191 Week 4")
        lbl.setStyleSheet(f"color: {COLORS['accent']}; font-size: 13px; font-weight: bold; background: transparent;")
        h.addWidget(lbl)
        h.addStretch()
        cat = QSvgWidget()
        cat.load(QByteArray(CAT_SVG))
        cat.setFixedSize(36, 36)
        cat.setStyleSheet("background: transparent;")
        fx = QGraphicsOpacityEffect(cat)
        fx.setOpacity(0.85)
        cat.setGraphicsEffect(fx)
        h.addWidget(cat)
        return w

    def _make_footer(self, text: str) -> QLabel:
        lbl = QLabel(text or "PySide6 · TensorFlow/Keras · Matplotlib")
        lbl.setStyleSheet(
            f"background: {COLORS['panel']}; color: {COLORS['text_muted']}; "
            f"font-size: 10px; padding: 5px 12px; "
            f"border-top: 1px solid {COLORS['border']};"
        )
        return lbl

    def _make_card(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['panel']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        return f

    def _make_left_panel(self) -> QFrame:
        card = self._make_card()
        card.setFixedWidth(215)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        self._add_section_label(layout, "⚙  Parameters")
        for field, key in [("Hidden Layers", "layers"), ("Epochs", "epochs"), ("Learning Rate", "lr")]:
            self._add_field_label(layout, field)
            inp = QLineEdit(str(self.DEFAULT_PARAMS[key]))
            inp.setStyleSheet(self._input_qss())
            layout.addWidget(inp)
            setattr(self, f"_inp_{field.lower().replace(' ', '_')}", inp)

        self._add_field_label(layout, "Activation")
        self._inp_activation = QComboBox()
        self._inp_activation.addItems(["relu", "tanh", "sigmoid", "elu"])
        self._inp_activation.setCurrentText(str(self.DEFAULT_PARAMS["activation"]))
        self._inp_activation.setStyleSheet(self._combo_qss())
        layout.addWidget(self._inp_activation)

        custom = self._build_custom_controls()
        if custom is not None:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet(f"color: {COLORS['border']}; background: {COLORS['border']}; max-height: 1px;")
            layout.addWidget(sep)
            layout.addWidget(custom)

        layout.addStretch()

        for label, color, attr in [
            ("▶  Train", COLORS["accent"], "_btn_train"),
            ("⏹  Stop",  COLORS["danger"], "_btn_stop"),
            ("↺  Reset", COLORS["card"],   "_btn_reset"),
        ]:
            btn = QPushButton(label)
            tc = COLORS["bg"] if attr != "_btn_reset" else COLORS["text_dim"]
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color}; color: {tc};
                    border: none; border-radius: 4px;
                    padding: 6px; font-size: 11px; font-weight: bold;
                }}
                QPushButton:disabled {{ opacity: 0.4; }}
            """)
            layout.addWidget(btn)
            setattr(self, attr, btn)

        self._btn_train.clicked.connect(self._on_train_clicked)
        self._btn_stop.clicked.connect(self._on_stop_clicked)
        self._btn_reset.clicked.connect(self._on_reset_clicked)
        self._btn_stop.setEnabled(False)

        self._epoch_bar = QProgressBar()
        self._epoch_bar.setRange(0, 100)
        self._epoch_bar.setValue(0)
        self._epoch_bar.setTextVisible(False)
        self._epoch_bar.setFixedHeight(6)
        self._epoch_bar.setStyleSheet(f"""
            QProgressBar {{ background: {COLORS['card']}; border-radius: 3px; border: none; }}
            QProgressBar::chunk {{ background: {COLORS['success']}; border-radius: 3px; }}
        """)
        layout.addWidget(self._epoch_bar)

        self._epoch_label = QLabel("Ready")
        self._epoch_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; background: transparent;")
        layout.addWidget(self._epoch_label)

        return card

    def _make_right_panel(self) -> QFrame:
        card = self._make_card()
        card.setFixedWidth(175)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        self._add_section_label(layout, "📊  Training")
        self._stat_labels: dict[str, QLabel] = {}
        for key, color in [("Train Loss", COLORS["danger"]), ("Val Loss", COLORS["accent"]), ("MAE", COLORS["success"])]:
            self._add_field_label(layout, key)
            v = QLabel("—")
            v.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px; background: transparent;")
            layout.addWidget(v)
            self._stat_labels[key] = v

        self.loss_canvas = MatplotlibCanvas(nrows=1, ncols=1)
        self.loss_canvas.setFixedHeight(90)
        layout.addWidget(self.loss_canvas)

        custom_info = self._build_custom_info()
        if custom_info is not None:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet(f"color: {COLORS['border']}; background: {COLORS['border']}; max-height: 1px;")
            layout.addWidget(sep)
            layout.addWidget(custom_info)

        layout.addStretch()
        return card

    # ── Style helpers ────────────────────────────────────────────────

    def _add_section_label(self, layout, text: str):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {COLORS['accent']}; font-weight: bold; font-size: 12px; background: transparent;")
        layout.addWidget(lbl)

    def _add_field_label(self, layout, text: str):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px; background: transparent;")
        layout.addWidget(lbl)

    def _input_qss(self) -> str:
        return f"""
            QLineEdit {{
                background: {COLORS['card']}; color: {COLORS['text']};
                border: 1px solid {COLORS['border_light']}; border-radius: 4px;
                padding: 4px 6px; font-size: 11px;
            }}
        """

    def _combo_qss(self) -> str:
        return f"""
            QComboBox {{
                background: {COLORS['card']}; color: {COLORS['text']};
                border: 1px solid {COLORS['border_light']}; border-radius: 4px;
                padding: 4px 6px; font-size: 11px;
            }}
            QComboBox QAbstractItemView {{
                background: {COLORS['card']}; color: {COLORS['text']};
                selection-background-color: {COLORS['accent']};
            }}
        """

    # ── Abstract interface (subclasses implement) ────────────────────

    def _build_custom_controls(self) -> QWidget | None:
        return None

    def _build_main_chart(self) -> QWidget:
        raise NotImplementedError("Subclass must implement _build_main_chart()")

    def _build_custom_info(self) -> QWidget | None:
        return None

    def _get_model_and_data(self) -> tuple:
        """Return (keras.Model, x_train: ndarray, y_train: ndarray)."""
        raise NotImplementedError("Subclass must implement _get_model_and_data()")

    def _on_train_complete(self, history):
        """Called when training finishes. Override to update main chart."""
        self._epoch_label.setText("Done ✓")
        self._btn_train.setEnabled(True)
        self._btn_stop.setEnabled(False)

    def _reset_custom(self):
        """Hook for subclasses to reset their own state on Reset."""
        pass

    # ── Slot handlers ────────────────────────────────────────────────

    def _on_epoch_done(self, epoch: int, logs: dict):
        pct = int((epoch + 1) / self._total_epochs * 100)
        self._epoch_bar.setValue(pct)
        self._epoch_label.setText(f"Epoch {epoch + 1} / {self._total_epochs}")

        loss = logs.get("loss", 0.0)
        val_loss = logs.get("val_loss", 0.0)
        mae = logs.get("mae", logs.get("mean_absolute_error", 0.0))
        self._stat_labels["Train Loss"].setText(f"{loss:.5f}")
        self._stat_labels["Val Loss"].setText(f"{val_loss:.5f}")
        self._stat_labels["MAE"].setText(f"{mae:.4f}")

        self._loss_history["loss"].append(loss)
        self._loss_history["val_loss"].append(val_loss)
        ax = self.loss_canvas.ax
        ax.cla()
        ax.set_facecolor(COLORS["bg"])
        ax.plot(self._loss_history["loss"], color=COLORS["danger"], linewidth=1)
        ax.plot(self._loss_history["val_loss"], color=COLORS["accent"], linewidth=1)
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
            self._epoch_label.setText(f"Error: {exc}")
            return

        self._current_model = model
        self._total_epochs = int(self._inp_epochs.text())

        self._worker = TrainWorker(model, x_train, y_train,
                                   self._total_epochs, val_split=0.1)
        self._worker.epoch_done.connect(self._on_epoch_done)
        self._worker.train_done.connect(self._on_train_complete)
        self._worker.train_error.connect(
            lambda e: self._epoch_label.setText(f"Error: {e}")
        )
        self._worker.start()
        self._btn_train.setEnabled(False)
        self._btn_stop.setEnabled(True)
        self._epoch_label.setText("Training…")

    def _on_stop_clicked(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
        self._btn_train.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._epoch_label.setText("Stopped")

    def _on_reset_clicked(self):
        self._on_stop_clicked()
        self._inp_hidden_layers.setText(str(self.DEFAULT_PARAMS["layers"]))
        self._inp_epochs.setText(str(self.DEFAULT_PARAMS["epochs"]))
        self._inp_learning_rate.setText(str(self.DEFAULT_PARAMS["lr"]))
        self._inp_activation.setCurrentText(str(self.DEFAULT_PARAMS["activation"]))
        for lbl in self._stat_labels.values():
            lbl.setText("—")
        self._epoch_bar.setValue(0)
        self._epoch_label.setText("Ready")
        self._loss_history = {"loss": [], "val_loss": []}
        self.loss_canvas.clear()
        self.loss_canvas.draw()
        self._reset_custom()

    # ── Helpers ──────────────────────────────────────────────────────

    def _parse_layers(self) -> list[int]:
        import ast
        text = self._inp_hidden_layers.text().strip()
        result = ast.literal_eval(text)
        return [result] if isinstance(result, int) else list(result)

    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()
        super().closeEvent(event)
