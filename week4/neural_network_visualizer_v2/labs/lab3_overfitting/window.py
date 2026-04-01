import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from shared.base_lab_window import BaseLabWindow, _label_qss
from shared.matplotlib_canvas import MatplotlibCanvas
from shared.train_worker import TrainWorker
from shared.colors import COLORS, STAGE_COLORS
from .model import make_data, make_model, MODEL_CONFIGS

_STAGE_ORDER = ["Underfit", "Good Fit", "Overfit"]


class Lab3Window(BaseLabWindow):
    DEFAULT_PARAMS = {
        "layers": "N/A (preset)",
        "activation": "relu",
        "epochs": 200,
        "lr": 0.001,
    }

    def __init__(self, parent=None):
        self._x_tr, self._y_tr, self._x_plot, self._y_true = make_data()
        self._trained: dict[str, np.ndarray] = {}
        self._stage_idx = 0
        super().__init__(
            title="Lab 3 · 과적합 데모",
            footer_text="3 models: Underfit [4] · Good Fit [32,16]+Dropout · Overfit [256,128,64,32]",
            parent=parent,
        )

    def _build_custom_controls(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._add_section_label(layout, "MODELS")
        self._stage_lbl = QLabel("—")
        self._stage_lbl.setStyleSheet(_label_qss(COLORS["accent"], 9))
        layout.addWidget(self._stage_lbl)
        return w

    def _build_main_chart(self) -> QWidget:
        self._main_canvas = MatplotlibCanvas(nrows=1, ncols=1)
        return self._main_canvas

    def _build_custom_info(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._add_section_label(layout, "LOSS GAP")
        self._gap_labels: dict[str, QLabel] = {}
        for name in _STAGE_ORDER:
            self._add_field_label(layout, name)
            v = QLabel("—")
            v.setStyleSheet(_label_qss(STAGE_COLORS[name], 10, bold=True))
            layout.addWidget(v)
            self._gap_labels[name] = v
        return w

    def _get_model_and_data(self) -> tuple:
        name = _STAGE_ORDER[0]
        model = make_model(name, float(self._inp_learning_rate.text()))
        return model, self._x_tr, self._y_tr

    def _on_train_clicked(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()
        self._trained = {}
        self._stage_idx = 0
        self._loss_history = {"loss": [], "val_loss": []}
        self._epoch_bar.setValue(0)
        self._btn_train.setEnabled(False)
        self._btn_stop.setEnabled(True)
        self._nn_diagram.set_training(True)
        self._start_stage(0)

    def _start_stage(self, idx: int):
        name = _STAGE_ORDER[idx]
        self._stage_lbl.setText(f"TRAINING: {name.upper()}…")
        self._current_stage_name = name
        self._total_epochs = int(self._inp_epochs.text())
        model = make_model(name, float(self._inp_learning_rate.text()))
        self._current_model = model
        self._worker = TrainWorker(model, self._x_tr, self._y_tr,
                                   self._total_epochs, val_split=0.1)
        self._worker.epoch_done.connect(self._on_epoch_done)
        self._worker.train_done.connect(self._on_stage_done)
        self._worker.train_error.connect(
            lambda e: self._epoch_label.setText(f"ERROR: {e}")
        )
        self._worker.start()

    def _on_stage_done(self, history):
        name = self._current_stage_name
        x_in = self._x_plot.reshape(-1, 1).astype(np.float32)
        self._trained[name] = self._current_model.predict(x_in, verbose=0).flatten()

        logs = history.history
        tl = logs["loss"][-1]
        vl = logs.get("val_loss", [tl])[-1]
        self._gap_labels[name].setText(f"T:{tl:.4f}  V:{vl:.4f}")

        self._stage_idx += 1
        if self._stage_idx < len(_STAGE_ORDER):
            self._loss_history = {"loss": [], "val_loss": []}
            self._start_stage(self._stage_idx)
        else:
            self._on_all_stages_done()

    def _on_all_stages_done(self):
        self._epoch_label.setText("DONE ✓")
        self._btn_train.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._stage_lbl.setText("ALL 3 MODELS TRAINED")
        self._nn_diagram.set_training(False)
        self._draw_comparison()

    def _draw_comparison(self):
        ax = self._main_canvas.ax
        ax.cla()
        ax.set_facecolor(COLORS["bg"])
        ax.scatter(self._x_tr.flatten(), self._y_tr.flatten(),
                   color=COLORS["text_muted"], s=6, alpha=0.4, label="Data")
        ax.plot(self._x_plot, self._y_true,
                color=COLORS["text_dim"], linewidth=1.5, linestyle=":", label="True fn", alpha=0.6)
        for name, y_pred in self._trained.items():
            ax.plot(self._x_plot, y_pred,
                    color=STAGE_COLORS[name], linewidth=1.8, label=name)
        ax.legend(facecolor=COLORS["card"], edgecolor=COLORS["border"],
                  labelcolor=COLORS["text_dim"], fontsize=9,
                  prop={"family": "Consolas", "size": 9})
        ax.set_title("OVERFITTING COMPARISON",
                     color=COLORS["accent"], fontsize=10, fontfamily="Consolas")
        for sp in ax.spines.values():
            sp.set_edgecolor(COLORS["border"])
        ax.tick_params(colors=COLORS["text_muted"])
        ax.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.5)
        self._main_canvas.draw()

    def _reset_custom(self):
        self._trained = {}
        self._stage_idx = 0
        self._stage_lbl.setText("—")
        for v in self._gap_labels.values():
            v.setText("—")
        self._main_canvas.clear()
        self._main_canvas.draw()

    def _on_reset_clicked(self):
        self._on_stop_clicked()
        self._inp_epochs.setText(str(self.DEFAULT_PARAMS["epochs"]))
        self._inp_learning_rate.setText(str(self.DEFAULT_PARAMS["lr"]))
        for lbl in self._stat_labels.values():
            lbl.setText("—")
        self._epoch_bar.setValue(0)
        self._epoch_label.setText("READY")
        self._loss_history = {"loss": [], "val_loss": []}
        self.loss_canvas.clear()
        self.loss_canvas.draw()
        self._reset_custom()
