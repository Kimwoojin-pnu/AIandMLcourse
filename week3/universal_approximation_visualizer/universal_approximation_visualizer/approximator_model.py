"""approximator_model.py"""
import numpy as np


def _tanh(x): return np.tanh(x)
def _tanh_d(x): return 1.0 - np.tanh(x)**2


TARGET_FUNCTIONS = {
    "Sine Wave":       lambda x: np.sin(2 * np.pi * x),
    "Step Function":   lambda x: np.where(x < 0.5, 0.0, 1.0),
    "Complex":         lambda x: np.sin(2*np.pi*x) + 0.5*np.sin(4*np.pi*x) + 0.3*np.cos(6*np.pi*x),
}

X_TRAIN = np.linspace(0, 1, 100).reshape(-1, 1)
X_TEST  = np.linspace(0, 1, 200).reshape(-1, 1)


class UniversalApproximator:
    def __init__(self, n_hidden: int = 10, lr: float = 0.01):
        self.n_hidden = n_hidden
        self.lr = lr
        self.loss_history: list[float] = []
        self.step = 0
        self._init()

    def _init(self):
        lim = np.sqrt(6 / (1 + self.n_hidden))
        self.W1 = np.random.uniform(-lim, lim, (1, self.n_hidden))
        self.b1 = np.zeros(self.n_hidden)
        lim2 = np.sqrt(6 / (self.n_hidden + 1))
        self.W2 = np.random.uniform(-lim2, lim2, (self.n_hidden, 1))
        self.b2 = np.zeros(1)

    def reset(self, n_hidden: int | None = None, lr: float | None = None):
        if n_hidden is not None: self.n_hidden = n_hidden
        if lr is not None: self.lr = lr
        self.loss_history = []
        self.step = 0
        self._init()

    def forward(self, x: np.ndarray) -> np.ndarray:
        z1 = x @ self.W1 + self.b1
        a1 = _tanh(z1)
        return a1 @ self.W2 + self.b2

    def train_step(self, x: np.ndarray, y: np.ndarray) -> float:
        z1 = x @ self.W1 + self.b1
        a1 = _tanh(z1)
        out = a1 @ self.W2 + self.b2
        loss = float(np.mean((out - y)**2))

        dL = 2 * (out - y) / len(x)
        dW2 = a1.T @ dL
        db2 = np.sum(dL, axis=0)
        da1 = dL @ self.W2.T
        dz1 = da1 * _tanh_d(z1)
        dW1 = x.T @ dz1
        db1 = np.sum(dz1, axis=0)

        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1

        self.loss_history.append(loss)
        self.step += 1
        return loss

    def train_epochs(self, x, y, epochs: int):
        for _ in range(epochs):
            self.train_step(x, y)
