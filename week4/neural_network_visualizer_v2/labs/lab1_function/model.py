import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import numpy as np
import tensorflow as tf
from tensorflow import keras

FUNCTIONS = {
    "sin(x)":             lambda x: np.sin(x),
    "cos(x)+0.5sin(2x)":  lambda x: np.cos(x) + 0.5 * np.sin(2 * x),
    "x·sin(x)":           lambda x: x * np.sin(x),
}
X_LO, X_HI, N = -2 * np.pi, 2 * np.pi, 300


def make_data(func_name: str):
    x = np.linspace(X_LO, X_HI, N)
    idx = np.random.permutation(N)
    xs, ys = x[idx], FUNCTIONS[func_name](x[idx])
    return (
        xs.reshape(-1, 1).astype(np.float32),
        ys.reshape(-1, 1).astype(np.float32),
        x,
        FUNCTIONS[func_name](x),
    )


def make_model(layers: list[int], activation: str, lr: float) -> keras.Model:
    model = keras.Sequential()
    model.add(keras.layers.Input(shape=(1,)))
    for units in layers:
        model.add(keras.layers.Dense(units, activation=activation))
    model.add(keras.layers.Dense(1, activation="linear"))
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss="mse",
        metrics=["mae"],
    )
    return model
