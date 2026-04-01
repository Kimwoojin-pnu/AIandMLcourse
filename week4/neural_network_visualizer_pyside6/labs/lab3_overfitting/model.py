import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import numpy as np
import tensorflow as tf
from tensorflow import keras

N = 150

MODEL_CONFIGS = {
    "Underfit": {"layers": [4],                "dropout": 0.0},
    "Good Fit": {"layers": [32, 16],           "dropout": 0.2},
    "Overfit":  {"layers": [256, 128, 64, 32], "dropout": 0.0},
}


def make_data():
    rng = np.random.default_rng(0)
    x = np.linspace(-3, 3, N)
    y = np.sin(2 * x) + 0.5 * x + rng.normal(0, 0.3, N)
    idx = rng.permutation(N)
    x, y = x[idx], y[idx]
    return (
        x.reshape(-1, 1).astype(np.float32),
        y.reshape(-1, 1).astype(np.float32),
        np.linspace(-3, 3, 200),
        np.sin(2 * np.linspace(-3, 3, 200)) + 0.5 * np.linspace(-3, 3, 200),
    )


def make_model(config_name: str, lr: float) -> keras.Model:
    cfg = MODEL_CONFIGS[config_name]
    model = keras.Sequential()
    model.add(keras.layers.Input(shape=(1,)))
    for units in cfg["layers"]:
        model.add(keras.layers.Dense(units, activation="relu"))
        if cfg["dropout"] > 0:
            model.add(keras.layers.Dropout(cfg["dropout"]))
    model.add(keras.layers.Dense(1, activation="linear"))
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss="mse",
        metrics=["mae"],
    )
    return model
