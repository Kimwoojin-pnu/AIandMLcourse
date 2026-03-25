"""activation_model.py — 활성화 함수 순수 로직 (비-GUI)"""
import numpy as np


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

def sigmoid_deriv(x):
    s = sigmoid(x)
    return s * (1.0 - s)

def tanh_fn(x):
    return np.tanh(x)

def tanh_deriv(x):
    return 1.0 - np.tanh(x) ** 2

def relu(x):
    return np.maximum(0.0, x)

def relu_deriv(x):
    return np.where(x > 0, 1.0, 0.0)

def leaky_relu(x, alpha=0.01):
    return np.where(x > 0, x, alpha * x)

def leaky_relu_deriv(x, alpha=0.01):
    return np.where(x > 0, 1.0, alpha)


# 함수명 → (함수, 미분함수) — Leaky ReLU는 alpha 인자 있으므로 None 처리
FUNC_MAP: dict[str, tuple] = {
    "Sigmoid":    (sigmoid,    sigmoid_deriv),
    "Tanh":       (tanh_fn,    tanh_deriv),
    "ReLU":       (relu,       relu_deriv),
    "Leaky ReLU": (leaky_relu, leaky_relu_deriv),  # alpha 별도 전달
}

COLORS: dict[str, str] = {
    "Sigmoid":    "#e74c3c",
    "Tanh":       "#3498db",
    "ReLU":       "#2ecc71",
    "Leaky ReLU": "#f39c12",
}
