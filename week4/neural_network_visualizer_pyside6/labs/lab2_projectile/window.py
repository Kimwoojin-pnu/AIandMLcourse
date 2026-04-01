import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt
from shared.base_lab_window import BaseLabWindow
from shared.matplotlib_canvas import MatplotlibCanvas
from shared.colors import COLORS
from .model import make_data, make_model, true_trajectory


class Lab2Window(BaseLabWindow):
    DEFAULT_PARAMS = {
        "layers": "[128, 64, 32]",
        "activation": "relu",
        "epochs": 500,
        "lr": 0.001,
    }

    def __init__(self, parent=None):
        self._x_train, self._y_train = make_data()
        super().__init__(
            title="Lab 2 · 포물선 회귀",
            footer_text="Input: (v₀, θ, t) → Output: (x, y) · Dropout 0.1 · 500 epochs",
            parent=parent,
        )

    def _build_custom_controls(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._add_section_label(layout, "🎯  Trajectory Test")

        self._v0_lbl = QLabel("v₀ (m/s): 30")
        self._v0_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px; background: transparent;")
        layout.addWidget(self._v0_lbl)
        self._v0_slider = QSlider(Qt.Orientation.Horizontal)
        self._v0_slider.setRange(10, 50)
        self._v0_slider.setValue(30)
        self._v0_slider.valueChanged.connect(self._on_v0_changed)
        layout.addWidget(self._v0_slider)

        self._theta_lbl = QLabel("θ (°): 45")
        self._theta_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px; background: transparent;")
        layout.addWidget(self._theta_lbl)
        self._theta_slider = QSlider(Qt.Orientation.Horizontal)
        self._theta_slider.setRange(10, 80)
        self._theta_slider.setValue(45)
        self._theta_slider.valueChanged.connect(self._on_theta_changed)
        layout.addWidget(self._theta_slider)
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
        self._add_section_label(layout, "🔬  Error")
        self._err_labels: dict[str, QLabel] = {}
        for key in ["Height Err (m)", "Range Err (m)"]:
            self._add_field_label(layout, key)
            v = QLabel("—")
            v.setStyleSheet(f"color: {COLORS['highlight']}; font-weight: bold; font-size: 12px; background: transparent;")
            layout.addWidget(v)
            self._err_labels[key] = v
        return w

    def _get_model_and_data(self) -> tuple:
        model = make_model(self._parse_layers(),
                           self._inp_activation.currentText(),
                           float(self._inp_learning_rate.text()))
        return model, self._x_train, self._y_train

    def _on_train_complete(self, history):
        super()._on_train_complete(history)
        self._update_chart()

    def _on_v0_changed(self, v: int):
        self._v0_lbl.setText(f"v₀ (m/s): {v}")
        self._update_chart()

    def _on_theta_changed(self, v: int):
        self._theta_lbl.setText(f"θ (°): {v}")
        self._update_chart()

    def _update_chart(self):
        if self._current_model is None:
            return
        v0 = float(self._v0_slider.value())
        theta = float(self._theta_slider.value())
        t_arr, x_true, y_true = true_trajectory(v0, theta)
        inp = np.stack([
            np.full(len(t_arr), v0),
            np.full(len(t_arr), theta),
            t_arr,
        ], axis=1).astype(np.float32)
        pred = self._current_model.predict(inp, verbose=0)
        x_pred, y_pred = pred[:, 0], pred[:, 1]

        h_true, h_pred = float(np.max(y_true)), float(np.max(y_pred))
        r_true = float(x_true[-1])
        r_pred = float(x_pred[np.argmin(np.abs(y_pred))])
        self._err_labels["Height Err (m)"].setText(f"{abs(h_true - h_pred):.3f}")
        self._err_labels["Range Err (m)"].setText(f"{abs(r_true - r_pred):.3f}")

        ax = self._main_canvas.ax
        ax.cla()
        ax.set_facecolor(COLORS["bg"])
        ax.plot(x_true, y_true, color=COLORS["accent"], linewidth=2,
                label=f"True (v₀={v0:.0f}, θ={theta:.0f}°)", alpha=0.8)
        ax.plot(x_pred, y_pred, color=COLORS["danger"], linewidth=1.5,
                linestyle="--", label="Predicted")
        ax.set_xlabel("x (m)", color=COLORS["text_dim"])
        ax.set_ylabel("y (m)", color=COLORS["text_dim"])
        ax.legend(facecolor=COLORS["card"], edgecolor=COLORS["border"],
                  labelcolor=COLORS["text_dim"], fontsize=9)
        ax.set_title("Projectile Trajectory", color=COLORS["text_dim"], fontsize=10)
        for sp in ax.spines.values():
            sp.set_edgecolor(COLORS["border"])
        ax.tick_params(colors=COLORS["text_muted"])
        ax.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.5)
        self._main_canvas.draw()
