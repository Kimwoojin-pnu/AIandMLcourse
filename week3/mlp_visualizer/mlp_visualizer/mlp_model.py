"""mlp_model.py — MLP 순수 로직"""
import numpy as np


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

def _sigmoid_d(x):
    s = _sigmoid(x)
    return s * (1.0 - s)


class MLPModel:
    def __init__(self, hidden_size: int = 4, lr: float = 0.5):
        self.hidden_size = hidden_size
        self.lr = lr
        self.loss_history: list[float] = []
        self.epoch = 0
        self.dW1 = None
        self.dW2 = None
        self.a1 = None
        self._init_weights()

    def _init_weights(self):
        hs = self.hidden_size
        self.W1 = np.random.randn(2, hs) * np.sqrt(2.0 / 2)
        self.b1 = np.zeros((1, hs))
        self.W2 = np.random.randn(hs, 1) * np.sqrt(2.0 / hs)
        self.b2 = np.zeros((1, 1))

    def reset(self, hidden_size: int | None = None, lr: float | None = None):
        if hidden_size is not None:
            self.hidden_size = hidden_size
        if lr is not None:
            self.lr = lr
        self.loss_history = []
        self.epoch = 0
        self.dW1 = self.dW2 = self.a1 = None
        self._init_weights()

    def forward(self, X: np.ndarray) -> np.ndarray:
        self.z1 = X @ self.W1 + self.b1
        self.a1 = _sigmoid(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = _sigmoid(self.z2)
        return self.a2

    def train_step(self, X: np.ndarray, y: np.ndarray) -> float:
        m = X.shape[0]
        output = self.forward(X)
        loss = float(np.mean((output - y) ** 2))

        # Backward
        dz2 = output - y
        self.dW2 = (1/m) * self.a1.T @ dz2
        db2 = (1/m) * np.sum(dz2, axis=0, keepdims=True)

        da1 = dz2 @ self.W2.T
        dz1 = da1 * _sigmoid_d(self.z1)
        self.dW1 = (1/m) * X.T @ dz1
        db1 = (1/m) * np.sum(dz1, axis=0, keepdims=True)

        self.W2 -= self.lr * self.dW2
        self.b2 -= self.lr * db2
        self.W1 -= self.lr * self.dW1
        self.b1 -= self.lr * db1

        self.loss_history.append(loss)
        self.epoch += 1
        return loss

    def predict(self, X: np.ndarray) -> np.ndarray:
        return (self.forward(X) > 0.5).astype(int)

    def accuracy(self, X: np.ndarray, y: np.ndarray) -> float:
        return float(np.mean(self.predict(X) == y.astype(int)))
