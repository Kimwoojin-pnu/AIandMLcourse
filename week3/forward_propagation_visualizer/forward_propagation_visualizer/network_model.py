"""network_model.py — SimpleNetwork 순수 로직"""
from dataclasses import dataclass
import numpy as np


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

def _relu(x):
    return np.maximum(0.0, x)


@dataclass
class ForwardResult:
    z1: np.ndarray   # (3,) before ReLU
    a1: np.ndarray   # (3,) after ReLU
    z2: float        # before Sigmoid
    a2: float        # output


class SimpleNetwork:
    """2→3→1 네트워크 (고정 구조, 가중치만 무작위 변경 가능)"""

    def __init__(self, seed: int = 42):
        self._seed = seed
        self._rng = np.random.default_rng(seed)
        self.W1: np.ndarray  # (2, 3)
        self.b1: np.ndarray  # (3,)
        self.W2: np.ndarray  # (3, 1)
        self.b2: np.ndarray  # (1,)
        self.randomize(seed)

    def randomize(self, seed: int | None = None):
        rng = np.random.default_rng(seed)
        self.W1 = rng.standard_normal((2, 3)) * 0.5
        self.b1 = rng.standard_normal(3) * 0.1
        self.W2 = rng.standard_normal((3, 1)) * 0.5
        self.b2 = rng.standard_normal(1) * 0.1

    def forward(self, x1: float, x2: float) -> ForwardResult:
        X = np.array([x1, x2])
        z1 = self.W1.T @ X + self.b1          # (3,)
        a1 = _relu(z1)                          # (3,)
        z2 = float((self.W2.T @ a1 + self.b2)[0])
        a2 = float(_sigmoid(z2))
        return ForwardResult(z1=z1, a1=a1, z2=z2, a2=a2)
