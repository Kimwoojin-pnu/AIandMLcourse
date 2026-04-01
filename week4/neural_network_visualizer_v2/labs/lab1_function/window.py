import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from shared.base_lab_window import BaseLabWindow, _label_qss
from shared.matplotlib_canvas import MatplotlibCanvas
from shared.colors import COLORS
from .model import FUNCTIONS, make_data, make_model


class Lab1Window(BaseLabWindow):
    DEFAULT_PARAMS = {
        "layers": "[128, 128, 64]",
        "activation": "tanh",
        "epochs": 1000,
        "lr": 0.001,
    }

    def __init__(self, parent=None):
        self._x_plot = np.array([])
        self._y_true = np.array([])
        super().__init__(
            title="Lab 1 · 함수 근사",
            footer_text="Layers=[128,128,64] · tanh · 1000 epochs · x∈[-2π, 2π]",
            parent=parent,
        )

    def _build_custom_controls(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._add_section_label(layout, "LAB CONTROLS")
        self._add_field_label(layout, "Function")
        self._fn_combo = QComboBox()
        self._fn_combo.addItems(list(FUNCTIONS.keys()))
        self._fn_combo.setStyleSheet(self._combo_qss())
        layout.addWidget(self._fn_combo)
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
        self._add_section_label(layout, "RESULTS")
        self._result_labels: dict[str, QLabel] = {}
        for key in ["MSE", "R²"]:
            self._add_field_label(layout, key)
            v = QLabel("—")
            v.setStyleSheet(_label_qss(COLORS["highlight"], 11, bold=True))
            layout.addWidget(v)
            self._result_labels[key] = v
        return w

    def _get_model_and_data(self) -> tuple:
        fn = self._fn_combo.currentText()
        x_tr, y_tr, self._x_plot, self._y_true = make_data(fn)
        model = make_model(self._parse_layers(),
                           self._inp_activation.currentText(),
                           float(self._inp_learning_rate.text()))
        return model, x_tr, y_tr

    def _on_train_complete(self, history):
        super()._on_train_complete(history)
        if self._current_model is None:
            return
        x_in = self._x_plot.reshape(-1, 1).astype(np.float32)
        y_pred = self._current_model.predict(x_in, verbose=0).flatten()

        mse = float(np.mean((self._y_true - y_pred) ** 2))
        ss_res = float(np.sum((self._y_true - y_pred) ** 2))
        ss_tot = float(np.sum((self._y_true - np.mean(self._y_true)) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
        self._result_labels["MSE"].setText(f"{mse:.6f}")
        self._result_labels["R²"].setText(f"{r2:.4f}")

        ax = self._main_canvas.ax
        ax.cla()
        ax.set_facecolor(COLORS["bg"])
        ax.plot(self._x_plot, self._y_true,
                color=COLORS["info"], linewidth=2, label="True", alpha=0.9)
        ax.plot(self._x_plot, y_pred,
                color=COLORS["accent"], linewidth=1.8, linestyle="--", label="Predicted")
        ax.legend(facecolor=COLORS["card"], edgecolor=COLORS["border"],
                  labelcolor=COLORS["text_dim"], fontsize=9,
                  prop={"family": "Consolas", "size": 9})
        ax.set_title(f"{self._fn_combo.currentText()}",
                     color=COLORS["accent"], fontsize=10,
                     fontfamily="Consolas")
        for sp in ax.spines.values():
            sp.set_edgecolor(COLORS["border"])
        ax.tick_params(colors=COLORS["text_muted"])
        ax.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.5)
        self._main_canvas.draw()
