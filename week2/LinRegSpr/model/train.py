"""
SpringModel — TensorFlow neural network that learns Hooke's Law: x = mg / k

Architecture : Dense(64, ReLU) → BN → Dense(32, ReLU) → Dense(16, ReLU) → Dense(1)
Loss         : Huber (robust to outlier noise)
Optimiser    : Adam with ReduceLROnPlateau
Plots saved  : output/training_data.png, loss_history.png, predictions.png,
               spring_physics.png, dashboard.png
"""

import os
import json
import numpy as np
import tensorflow as tf

import matplotlib
matplotlib.use("Agg")                          # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── Colour palette (dark GitHub-style theme) ──────────────────────────────────
BG     = "#0d1117"
PANEL  = "#161b22"
CYAN   = "#00d4ff"
PURPLE = "#7c3aed"
GREEN  = "#10b981"
ORANGE = "#f97316"
WHITE  = "#e6edf3"
GRAY   = "#8b949e"
DPI    = 150


def _style_axes(ax, title="", xlabel="", ylabel=""):
    """Apply consistent dark-theme style to a matplotlib Axes."""
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=WHITE, which="both")
    for sp in ax.spines.values():
        sp.set_color(GRAY)
        sp.set_linewidth(0.6)
    if title:
        ax.set_title(title, color=WHITE, fontsize=13, fontweight="bold", pad=10)
    if xlabel:
        ax.set_xlabel(xlabel, color=GRAY, fontsize=11)
    if ylabel:
        ax.set_ylabel(ylabel, color=GRAY, fontsize=11)
    ax.grid(color="#21262d", linewidth=0.5, linestyle="--", alpha=0.8)
    ax.tick_params(colors=WHITE)
    return ax


class SpringModel:
    """
    TensorFlow model that learns the linear mapping  mass → spring elongation
    implied by Hooke's Law  (F = kx  →  x = mg/k).

    Parameters
    ----------
    k         : spring constant [N/m]
    g         : gravitational acceleration [m/s²]
    noise_std : Gaussian noise std added to training labels [m]
    seed      : random seed for reproducibility
    """

    def __init__(
        self,
        k: float = 50.0,
        g: float = 9.81,
        noise_std: float = 0.003,
        seed: int = 42,
    ):
        self.k = k
        self.g = g
        self.noise_std = noise_std
        self.seed = seed
        self.model: tf.keras.Model | None = None
        self.history: tf.keras.callbacks.History | None = None

        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

        self._generate_data()
        self._build_model()

    # ── Data ─────────────────────────────────────────────────────────────────

    def _generate_data(self) -> None:
        np.random.seed(self.seed)
        masses = np.linspace(0.05, 3.0, 400)
        elongations = (masses * self.g) / self.k          # Hooke's Law
        noise = np.random.normal(0.0, self.noise_std, len(masses))

        self.masses_all             = masses
        self.elongations_theoretical = elongations
        self.elongations_noisy       = elongations + noise

        self.X = masses.reshape(-1, 1).astype(np.float32)
        self.y = self.elongations_noisy.reshape(-1, 1).astype(np.float32)

    # ── Model ────────────────────────────────────────────────────────────────

    def _build_model(self) -> None:
        tf.random.set_seed(self.seed)
        self.model = tf.keras.Sequential(
            [
                tf.keras.layers.InputLayer(shape=(1,), name="mass_kg"),
                tf.keras.layers.Dense(
                    64,
                    activation="relu",
                    name="hidden_1",
                    kernel_regularizer=tf.keras.regularizers.l2(1e-4),
                ),
                tf.keras.layers.BatchNormalization(name="bn_1"),
                tf.keras.layers.Dense(
                    32,
                    activation="relu",
                    name="hidden_2",
                    kernel_regularizer=tf.keras.regularizers.l2(1e-4),
                ),
                tf.keras.layers.Dense(16, activation="relu", name="hidden_3"),
                tf.keras.layers.Dense(1, name="elongation_m"),
            ],
            name="HooksLawNet",
        )
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss="huber",
            metrics=["mae", "mse"],
        )

    # ── Training ─────────────────────────────────────────────────────────────

    def train(self, epochs: int = 500, batch_size: int = 32, val_split: float = 0.2):
        """Train the model and persist the history to JSON."""
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=60,
                restore_best_weights=True,
                min_delta=1e-7,
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.5,
                patience=30,
                min_lr=1e-7,
                verbose=0,
            ),
        ]
        self.history = self.model.fit(
            self.X,
            self.y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=val_split,
            callbacks=callbacks,
            shuffle=True,
            verbose=0,
        )
        # Persist loss history so the frontend can render interactive charts
        hist = {
            "loss":    [float(v) for v in self.history.history["loss"]],
            "val_loss":[float(v) for v in self.history.history["val_loss"]],
            "mae":     [float(v) for v in self.history.history["mae"]],
            "val_mae": [float(v) for v in self.history.history["val_mae"]],
        }
        with open(os.path.join(self.output_dir, "training_history.json"), "w") as f:
            json.dump(hist, f, indent=2)
        return self.history

    # ── Inference ────────────────────────────────────────────────────────────

    def predict(self, mass: float) -> float:
        x = np.array([[mass]], dtype=np.float32)
        return float(self.model.predict(x, verbose=0)[0][0])

    def get_info(self) -> dict:
        if self.history is None:
            return {}
        return {
            "final_loss":    float(self.history.history["loss"][-1]),
            "final_mae":     float(self.history.history["mae"][-1]),
            "final_val_mae": float(self.history.history["val_mae"][-1]),
            "k":             self.k,
            "g":             self.g,
            "epochs_run":    len(self.history.history["loss"]),
            "model_params":  int(self.model.count_params()),
            "architecture":  [l.name for l in self.model.layers],
        }

    # ── Plots ─────────────────────────────────────────────────────────────────

    def save_plots(self) -> None:
        """Generate and save all analysis plots to output/."""
        self._plot_training_data()
        self._plot_loss_history()
        self._plot_predictions()
        self._plot_spring_physics()
        self._plot_dashboard()
        print(f"[SpringModel] All plots saved to '{self.output_dir}/'")

    # ── Plot 1: Training dataset ──────────────────────────────────────────────

    def _plot_training_data(self) -> None:
        fig, ax = plt.subplots(figsize=(11, 6), facecolor=BG)
        _style_axes(
            ax,
            title="Hooke's Law — Training Dataset",
            xlabel="Mass  m  (kg)",
            ylabel="Elongation  x  (m)",
        )
        ax.scatter(
            self.masses_all,
            self.elongations_noisy,
            color=CYAN,
            alpha=0.35,
            s=14,
            label=f"Measurements  (σ = {self.noise_std*1000:.0f} mm noise)",
            zorder=2,
        )
        ax.plot(
            self.masses_all,
            self.elongations_theoretical,
            color=ORANGE,
            linewidth=2.5,
            label=f"Theoretical  x = mg/k   (k = {self.k} N/m)",
            zorder=3,
        )
        ax.annotate(
            f"k = {self.k} N/m\ng = {self.g} m/s²\nN = {len(self.masses_all)} samples",
            xy=(0.04, 0.70),
            xycoords="axes fraction",
            color=WHITE,
            fontsize=10,
            bbox=dict(
                boxstyle="round,pad=0.5",
                facecolor="#21262d",
                edgecolor=GRAY,
                alpha=0.9,
            ),
        )
        ax.legend(facecolor=PANEL, edgecolor=GRAY, labelcolor=WHITE, fontsize=10)
        fig.tight_layout()
        fig.savefig(
            os.path.join(self.output_dir, "training_data.png"),
            dpi=DPI,
            bbox_inches="tight",
        )
        plt.close(fig)

    # ── Plot 2: Loss history ──────────────────────────────────────────────────

    def _plot_loss_history(self) -> None:
        epochs   = range(1, len(self.history.history["loss"]) + 1)
        loss     = self.history.history["loss"]
        val_loss = self.history.history["val_loss"]
        mae      = self.history.history["mae"]
        val_mae  = self.history.history["val_mae"]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor=BG)
        fig.suptitle(
            "Model Training Metrics",
            color=WHITE,
            fontsize=16,
            fontweight="bold",
            y=1.01,
        )

        # ── Huber loss ──
        _style_axes(ax1, "Training vs Validation Loss (Huber)", "Epoch", "Huber Loss")
        ax1.plot(epochs, loss,     color=CYAN,   linewidth=2.0, label="Train",      alpha=0.9)
        ax1.plot(epochs, val_loss, color=ORANGE, linewidth=2.0, label="Validation", alpha=0.9)
        ax1.fill_between(epochs, loss, val_loss, alpha=0.06, color=PURPLE)
        ax1.set_yscale("log")
        ax1.legend(facecolor=PANEL, edgecolor=GRAY, labelcolor=WHITE, fontsize=10)
        ax1.annotate(
            f"Final: {loss[-1]:.2e}",
            xy=(list(epochs)[-1], loss[-1]),
            xytext=(-70, 25),
            textcoords="offset points",
            color=CYAN,
            fontsize=9,
            arrowprops=dict(arrowstyle="->", color=CYAN, lw=1.2),
        )

        # ── MAE ──
        _style_axes(ax2, "Mean Absolute Error", "Epoch", "MAE  (m)")
        ax2.plot(epochs, mae,     color=GREEN,  linewidth=2.0, label="Train MAE", alpha=0.9)
        ax2.plot(epochs, val_mae, color=PURPLE, linewidth=2.0, label="Val MAE",   alpha=0.9)
        ax2.legend(facecolor=PANEL, edgecolor=GRAY, labelcolor=WHITE, fontsize=10)
        ax2.annotate(
            f"Final: {mae[-1]*1000:.3f} mm",
            xy=(list(epochs)[-1], mae[-1]),
            xytext=(-90, 25),
            textcoords="offset points",
            color=GREEN,
            fontsize=9,
            arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.2),
        )

        fig.tight_layout()
        fig.savefig(
            os.path.join(self.output_dir, "loss_history.png"),
            dpi=DPI,
            bbox_inches="tight",
        )
        plt.close(fig)

    # ── Plot 3: Prediction vs theory + residuals ──────────────────────────────

    def _plot_predictions(self) -> None:
        test_m  = np.linspace(0.05, 3.5, 500, dtype=np.float32)
        preds   = self.model.predict(test_m.reshape(-1, 1), verbose=0).flatten()
        theory  = (test_m * self.g) / self.k
        resid_mm = (preds - theory) * 1000.0

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor=BG)
        fig.suptitle(
            "Neural Network vs Hooke's Law",
            color=WHITE,
            fontsize=16,
            fontweight="bold",
            y=1.01,
        )

        # ── Prediction ──
        _style_axes(ax1, "Predictions vs Theoretical", "Mass  m  (kg)", "Elongation  x  (m)")
        ax1.scatter(
            self.masses_all, self.elongations_noisy,
            color=GRAY, alpha=0.2, s=10, label="Training data", zorder=1,
        )
        ax1.plot(test_m, theory, color=ORANGE, linewidth=2.5,
                 linestyle="--", label="Hooke's Law  (theoretical)", zorder=3)
        ax1.plot(test_m, preds,  color=CYAN,   linewidth=2.5,
                 label="HooksLawNet  prediction", zorder=4)
        ax1.legend(facecolor=PANEL, edgecolor=GRAY, labelcolor=WHITE, fontsize=10)

        # ── Residuals ──
        _style_axes(ax2, "Prediction Residuals  (NN − Theory)", "Mass  m  (kg)", "Residual  (mm)")
        ax2.axhline(0, color=GRAY, linestyle="--", linewidth=1.0)
        ax2.fill_between(test_m, resid_mm, color=PURPLE, alpha=0.55)
        ax2.plot(test_m, resid_mm, color=PURPLE, linewidth=1.5)
        max_r = float(np.max(np.abs(resid_mm)))
        ax2.annotate(
            f"Max |residual| = {max_r:.3f} mm",
            xy=(0.05, 0.92),
            xycoords="axes fraction",
            color=WHITE,
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#21262d", edgecolor=GRAY),
        )

        fig.tight_layout()
        fig.savefig(
            os.path.join(self.output_dir, "predictions.png"),
            dpi=DPI,
            bbox_inches="tight",
        )
        plt.close(fig)

    # ── Plot 4: Spring physics at various loads ───────────────────────────────

    def _plot_spring_physics(self) -> None:
        test_masses = [0.2, 0.5, 1.0, 1.5, 2.0, 2.5]
        fig, axes = plt.subplots(1, len(test_masses), figsize=(16, 7), facecolor=BG)
        fig.suptitle(
            "Spring Elongation at Different Loads — NN Prediction",
            color=WHITE,
            fontsize=14,
            fontweight="bold",
            y=1.02,
        )

        for ax, m in zip(axes, test_masses):
            ax.set_facecolor(PANEL)
            ax.set_xlim(-1.2, 1.2)
            ax.set_xticks([])
            ax.set_ylim(-1.0, 1.1)
            ax.spines[:].set_color(GRAY)
            ax.spines[:].set_linewidth(0.5)
            ax.grid(False)

            x_pred  = self.predict(m)
            x_theo  = (m * self.g) / self.k

            self._draw_spring(ax, x_pred)

            ax.set_title(f"{m} kg", color=WHITE, fontsize=12, fontweight="bold")
            ax.set_xlabel(
                f"NN:  {x_pred*100:.1f} cm\nTheory: {x_theo*100:.1f} cm",
                color=GREEN,
                fontsize=9,
            )

        fig.tight_layout()
        fig.savefig(
            os.path.join(self.output_dir, "spring_physics.png"),
            dpi=DPI,
            bbox_inches="tight",
        )
        plt.close(fig)

    @staticmethod
    def _draw_spring(ax, elongation_m: float, coils: int = 8, amp: float = 0.35) -> None:
        """Draw a helical spring in a matplotlib Axes."""
        top    = 0.95
        bottom = max(top - max(elongation_m, 0.05) * 2.2, -0.85)
        t = np.linspace(0, 1, coils * 40)
        x = amp * np.sin(2 * np.pi * coils * t)
        y = top + t * (bottom - top)
        ax.plot([0, 0], [top + 0.02, top + 0.08], color="#8b949e", linewidth=3)
        ax.plot(x, y, color=CYAN, linewidth=2.2)
        ax.plot(0, bottom, "o", color=ORANGE, markersize=12, zorder=5)

    # ── Plot 5: Summary dashboard ─────────────────────────────────────────────

    def _plot_dashboard(self) -> None:
        fig = plt.figure(figsize=(16, 10), facecolor=BG)
        gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

        ax_data = fig.add_subplot(gs[0, 0])
        ax_loss = fig.add_subplot(gs[0, 1])
        ax_pred = fig.add_subplot(gs[0, 2])
        ax_info = fig.add_subplot(gs[1, :])

        # ── Data mini-plot ──
        _style_axes(ax_data, "Training Data", "Mass (kg)", "Elongation (m)")
        ax_data.scatter(self.masses_all, self.elongations_noisy,
                        color=CYAN, alpha=0.3, s=8)
        ax_data.plot(self.masses_all, self.elongations_theoretical,
                     color=ORANGE, lw=1.8)

        # ── Loss mini-plot ──
        epochs = range(1, len(self.history.history["loss"]) + 1)
        _style_axes(ax_loss, "Huber Loss History", "Epoch", "Loss (log)")
        ax_loss.plot(epochs, self.history.history["loss"],     color=CYAN,   lw=1.8, label="Train")
        ax_loss.plot(epochs, self.history.history["val_loss"], color=ORANGE, lw=1.8, label="Val")
        ax_loss.set_yscale("log")
        ax_loss.legend(facecolor=PANEL, edgecolor=GRAY, labelcolor=WHITE, fontsize=8)

        # ── Prediction mini-plot ──
        test_m = np.linspace(0.05, 3.5, 300, dtype=np.float32)
        preds  = self.model.predict(test_m.reshape(-1, 1), verbose=0).flatten()
        theory = (test_m * self.g) / self.k
        _style_axes(ax_pred, "NN vs Theory", "Mass (kg)", "Elongation (m)")
        ax_pred.plot(test_m, theory, color=ORANGE, lw=1.8, linestyle="--", label="Theory")
        ax_pred.plot(test_m, preds,  color=CYAN,   lw=1.8, label="NN")
        ax_pred.legend(facecolor=PANEL, edgecolor=GRAY, labelcolor=WHITE, fontsize=8)

        # ── Info panel ──
        ax_info.set_facecolor(PANEL)
        ax_info.set_xticks([]); ax_info.set_yticks([])
        ax_info.spines[:].set_color(GRAY)
        info = self.get_info()
        lines = [
            "  HooksLawNet  —  Summary",
            "",
            f"  Spring constant  k  =  {self.k} N/m",
            f"  Gravitational acc g  =  {self.g} m/s²",
            f"  Training samples     =  {len(self.masses_all)}",
            f"  Epochs run           =  {info.get('epochs_run','—')}",
            f"  Final Huber loss     =  {info.get('final_loss', 0):.2e}",
            f"  Final MAE            =  {info.get('final_mae', 0)*1000:.4f} mm",
            f"  Val MAE              =  {info.get('final_val_mae', 0)*1000:.4f} mm",
            f"  Trainable params     =  {info.get('model_params', '—'):,}",
            "",
            "  Architecture :  mass(1) → Dense(64,ReLU) → BN → Dense(32,ReLU) → Dense(16,ReLU) → elongation(1)",
        ]
        ax_info.text(
            0.03, 0.5,
            "\n".join(lines),
            color=WHITE, fontsize=12, va="center",
            fontfamily="monospace",
            transform=ax_info.transAxes,
        )

        fig.suptitle(
            "Hooke's Law Neural Network — Dashboard",
            color=WHITE, fontsize=17, fontweight="bold", y=1.01,
        )
        fig.savefig(
            os.path.join(self.output_dir, "dashboard.png"),
            dpi=DPI,
            bbox_inches="tight",
        )
        plt.close(fig)
