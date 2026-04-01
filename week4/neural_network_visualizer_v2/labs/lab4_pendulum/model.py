import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import numpy as np
import tensorflow as tf
from tensorflow import keras

G = 9.8
N_SAMPLES = 2000


def theoretical_period(L: float, theta0_deg: float) -> float:
    theta0 = np.radians(theta0_deg)
    T0 = 2 * np.pi * np.sqrt(L / G)
    correction = (1 + (1 / 16) * theta0 ** 2 + (11 / 3072) * theta0 ** 4)
    return float(T0 * correction)


def rk4_simulate(L: float, theta0_deg: float,
                 dt: float = 0.02, t_max: float = 10.0):
    theta0 = np.radians(theta0_deg)
    t = np.arange(0, t_max, dt)
    theta = np.zeros(len(t))
    omega = np.zeros(len(t))
    theta[0] = theta0

    def d_omega(th):
        return -(G / L) * np.sin(th)

    for i in range(len(t) - 1):
        k1 = omega[i]
        l1 = d_omega(theta[i])
        k2 = omega[i] + 0.5 * dt * l1
        l2 = d_omega(theta[i] + 0.5 * dt * k1)
        k3 = omega[i] + 0.5 * dt * l2
        l3 = d_omega(theta[i] + 0.5 * dt * k2)
        k4 = omega[i] + dt * l3
        l4 = d_omega(theta[i] + dt * k3)
        theta[i + 1] = theta[i] + (dt / 6) * (k1 + 2*k2 + 2*k3 + k4)
        omega[i + 1] = omega[i] + (dt / 6) * (l1 + 2*l2 + 2*l3 + l4)

    return t, theta


def make_data():
    rng = np.random.default_rng(7)
    L = rng.uniform(0.2, 3.0, N_SAMPLES)
    theta0 = rng.uniform(5, 75, N_SAMPLES)
    T = np.array([theoretical_period(l, t) for l, t in zip(L, theta0)])
    X = np.stack([L, theta0], axis=1).astype(np.float32)
    Y = T.reshape(-1, 1).astype(np.float32)
    return X, Y


def make_model(layers: list[int], activation: str, lr: float) -> keras.Model:
    model = keras.Sequential()
    model.add(keras.layers.Input(shape=(2,)))
    for units in layers:
        model.add(keras.layers.Dense(units, activation=activation))
        model.add(keras.layers.Dropout(0.1))
    model.add(keras.layers.Dense(1, activation="linear"))
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss="mse",
        metrics=["mae"],
    )
    return model
