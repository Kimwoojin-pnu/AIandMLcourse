"""
perceptron_model.py
퍼셉트론(Perceptron) 핵심 로직 모델
"""
import numpy as np


class Perceptron:
    """
    단층 퍼셉트론 (Single-Layer Perceptron)

    수식: y = step(w1*x1 + w2*x2 + b)
    학습 규칙: w += η * (y_true - y_pred) * x
               b += η * (y_true - y_pred)
    """

    def __init__(self, learning_rate: float = 0.1):
        self.lr = learning_rate
        # history: list of dict {epoch, w1, w2, bias, accuracy}
        self.history: list[dict] = []
        self.weights = np.zeros(2)
        self.bias = 0.0
        self._init_weights()

    # ─────────────────────────────────────────
    # 초기화
    # ─────────────────────────────────────────
    def _init_weights(self):
        """가중치·편향 랜덤 초기화"""
        rng = np.random.default_rng()
        self.weights = rng.standard_normal(2) * 0.5
        self.bias = float(rng.standard_normal() * 0.5)

    def reset(self):
        """학습 기록 초기화 + 가중치 재설정"""
        self.history.clear()
        self._init_weights()

    # ─────────────────────────────────────────
    # 추론
    # ─────────────────────────────────────────
    @staticmethod
    def _step(x: float) -> int:
        """계단 함수 (Step Function)"""
        return 1 if x >= 0 else 0

    def net_input(self, inputs: np.ndarray) -> float:
        """가중합 계산: w·x + b"""
        return float(np.dot(inputs, self.weights) + self.bias)

    def predict_single(self, inputs: np.ndarray) -> int:
        """단일 샘플 예측"""
        return self._step(self.net_input(inputs))

    def predict_batch(self, X: np.ndarray) -> np.ndarray:
        """배치 예측"""
        return np.array([self.predict_single(x) for x in X])

    # ─────────────────────────────────────────
    # 학습
    # ─────────────────────────────────────────
    def train_one_epoch(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        1 에포크 학습 수행

        Parameters
        ----------
        X : (4, 2) 입력 행렬
        y : (4,)  정답 레이블

        Returns
        -------
        float : 정확도 (0.0 ~ 1.0)
        """
        for x_i, y_i in zip(X, y):
            pred = self.predict_single(x_i)
            error = int(y_i) - pred
            # 가중치·편향 갱신
            self.weights += self.lr * error * x_i
            self.bias    += self.lr * error

        # 에포크 정확도 기록
        preds = self.predict_batch(X)
        acc = float(np.mean(preds == y))
        self.history.append({
            "epoch":    len(self.history) + 1,
            "w1":       float(self.weights[0]),
            "w2":       float(self.weights[1]),
            "bias":     float(self.bias),
            "accuracy": acc,
        })
        return acc

    # ─────────────────────────────────────────
    # 프로퍼티 (편의)
    # ─────────────────────────────────────────
    @property
    def w1(self) -> float:
        return float(self.weights[0])

    @property
    def w2(self) -> float:
        return float(self.weights[1])

    @property
    def b(self) -> float:
        return float(self.bias)
