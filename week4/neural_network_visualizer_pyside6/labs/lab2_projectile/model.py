import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import numpy as np
import tensorflow as tf
from tensorflow import keras

G = 9.8
N_SAMPLES = 2000


def make_data():
    rng = np.random.default_rng(42)
    v0 = rng.uniform(10, 50, N_SAMPLES)
    theta = rng.uniform(10, 80, N_SAMPLES)
    t_max = 2 * v0 * np.sin(np.radians(theta)) / G
    t = rng.uniform(0, 1, N_SAMPLES) * t_max
    x = v0 * np.cos(np.radians(theta)) * t + rng.normal(0, 0.05, N_SAMPLES)
    y = (v0 * np.sin(np.radians(theta)) * t
         - 0.5 * G * t ** 2
         + rng.normal(0, 0.05, N_SAMPLES))
    X = np.stack([v0, theta, t], axis=1).astype(np.float32)
    Y = np.stack([x, y], axis=1).astype(np.float32)
    return X, Y


def make_model(layers: list[int], activation: str, lr: float) -> keras.Model:
    model = keras.Sequential()
    model.add(keras.layers.Input(shape=(3,)))
    for units in layers:
        model.add(keras.layers.Dense(units, activation=activation))
        model.add(keras.layers.Dropout(0.1))
    model.add(keras.layers.Dense(2, activation="linear"))
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss="mse",
        metrics=["mae"],
    )
    return model


def true_trajectory(v0: float, theta_deg: float, n_points: int = 100):
    theta = np.radians(theta_deg)
    t_flight = 2 * v0 * np.sin(theta) / G
    t = np.linspace(0, t_flight, n_points)
    x = v0 * np.cos(theta) * t
    y = v0 * np.sin(theta) * t - 0.5 * G * t ** 2
    return t, x, y
