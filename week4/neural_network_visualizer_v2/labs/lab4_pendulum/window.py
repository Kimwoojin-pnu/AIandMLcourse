import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt
from shared.base_lab_window import BaseLabWindow, _label_qss, _SLIDER_QSS
from shared.matplotlib_canvas import MatplotlibCanvas
from shared.colors import COLORS
from .model import make_data, make_model, theoretical_period, rk4_simulate


class Lab4Window(BaseLabWindow):
    DEFAULT_PARAMS = {
        "layers": "[64, 32, 16]",
        "activation": "relu",
        "epochs": 500,
        "lr": 0.001,
    }

    def __init__(self, parent=None):
        self._x_train, self._y_train = make_data()
        super().__init__(
            title="Lab 4 · 진자 예측",
            footer_text="Input: (L, θ₀) → T · RK4 Simulation · 500 epochs",
            parent=parent,
        )

    def _build_custom_controls(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._add_section_label(layout, "PENDULUM TEST")

        self._L_lbl = QLabel("Length L (m): 1.0")
        self._L_lbl.setStyleSheet(_label_qss(COLORS["text_dim"], 9))
        layout.addWidget(self._L_lbl)
        self._L_slider = QSlider(Qt.Orientation.Horizontal)
        self._L_slider.setRange(2, 30)
        self._L_slider.setValue(10)
        self._L_slider.setStyleSheet(_SLIDER_QSS)
        self._L_slider.valueChanged.connect(self._on_L_changed)
        layout.addWidget(self._L_slider)

        self._th_lbl = QLabel("Initial θ₀ (°): 30")
        self._th_lbl.setStyleSheet(_label_qss(COLORS["text_dim"], 9))
        layout.addWidget(self._th_lbl)
        self._th_slider = QSlider(Qt.Orientation.Horizontal)
        self._th_slider.setRange(5, 75)
        self._th_slider.setValue(30)
        self._th_slider.setStyleSheet(_SLIDER_QSS)
        self._th_slider.valueChanged.connect(self._on_theta_changed)
        layout.addWidget(self._th_slider)
        return w

    def _build_main_chart(self) -> QWidget:
        self._main_canvas = MatplotlibCanvas(nrows=1, ncols=2)
        return self._main_canvas

    def _build_custom_info(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._add_section_label(layout, "PERIOD")
        self._period_labels: dict[str, QLabel] = {}
        for key in ["Theory (s)", "Predicted (s)", "MAPE (%)"]:
            self._add_field_label(layout, key)
            v = QLabel("—")
            v.setStyleSheet(_label_qss(COLORS["highlight"], 11, bold=True))
            layout.addWidget(v)
            self._period_labels[key] = v
        return w

    def _get_model_and_data(self) -> tuple:
        model = make_model(self._parse_layers(),
                           self._inp_activation.currentText(),
                           float(self._inp_learning_rate.text()))
        return model, self._x_train, self._y_train

    def _on_train_complete(self, history):
        super()._on_train_complete(history)
        self._update_charts()

    def _on_L_changed(self, v: int):
        self._L_lbl.setText(f"Length L (m): {v / 10:.1f}")
        self._update_charts()

    def _on_theta_changed(self, v: int):
        self._th_lbl.setText(f"Initial θ₀ (°): {v}")
        self._update_charts()

    def _update_charts(self):
        if self._current_model is None:
            return
        L = self._L_slider.value() / 10.0
        theta0 = float(self._th_slider.value())

        angles = np.linspace(5, 75, 60)
        Ls = np.full(60, L)
        X_in = np.stack([Ls, angles], axis=1).astype(np.float32)
        T_pred = self._current_model.predict(X_in, verbose=0).flatten()
        T_theory = np.array([theoretical_period(L, a) for a in angles])

        T_pred_pt = float(self._current_model.predict(
            np.array([[L, theta0]], dtype=np.float32), verbose=0
        ))
        T_theory_pt = theoretical_period(L, theta0)
        mape = abs(T_theory_pt - T_pred_pt) / T_theory_pt * 100
        self._period_labels["Theory (s)"].setText(f"{T_theory_pt:.4f}")
        self._period_labels["Predicted (s)"].setText(f"{T_pred_pt:.4f}")
        self._period_labels["MAPE (%)"].setText(f"{mape:.2f}")

        t_sim, theta_sim = rk4_simulate(L, theta0)

        axes = self._main_canvas.axes
        ax1, ax2 = axes[0], axes[1]

        ax1.cla()
        ax1.set_facecolor(COLORS["bg"])
        ax1.plot(angles, T_theory, color=COLORS["info"], linewidth=2, label="Theory")
        ax1.plot(angles, T_pred, color=COLORS["accent"], linewidth=1.8,
                 linestyle="--", label="Predicted")
        ax1.axvline(theta0, color=COLORS["success"], linewidth=0.8, alpha=0.7)
        ax1.set_xlabel("θ₀ (°)", color=COLORS["text_dim"], fontfamily="Consolas")
        ax1.set_ylabel("T (s)", color=COLORS["text_dim"], fontfamily="Consolas")
        ax1.set_title(f"PERIOD VS ANGLE  L={L:.1f}m",
                      color=COLORS["accent"], fontsize=9, fontfamily="Consolas")
        ax1.legend(facecolor=COLORS["card"], edgecolor=COLORS["border"],
                   labelcolor=COLORS["text_dim"], fontsize=8,
                   prop={"family": "Consolas", "size": 8})
        for sp in ax1.spines.values():
            sp.set_edgecolor(COLORS["border"])
        ax1.tick_params(colors=COLORS["text_muted"])
        ax1.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.5)

        ax2.cla()
        ax2.set_facecolor(COLORS["bg"])
        ax2.plot(t_sim[:500], np.degrees(theta_sim[:500]),
                 color=COLORS["success"], linewidth=1.2)
        ax2.set_xlabel("t (s)", color=COLORS["text_dim"], fontfamily="Consolas")
        ax2.set_ylabel("θ (°)", color=COLORS["text_dim"], fontfamily="Consolas")
        ax2.set_title(f"RK4 SIMULATION  θ₀={theta0:.0f}°",
                      color=COLORS["accent"], fontsize=9, fontfamily="Consolas")
        for sp in ax2.spines.values():
            sp.set_edgecolor(COLORS["border"])
        ax2.tick_params(colors=COLORS["text_muted"])
        ax2.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.5)

        self._main_canvas.fig.tight_layout(pad=1.5)
        self._main_canvas.draw()

    def _reset_custom(self):
        self._L_slider.setValue(10)
        self._th_slider.setValue(30)
        for v in self._period_labels.values():
            v.setText("—")
        self._main_canvas.clear()
        self._main_canvas.draw()
