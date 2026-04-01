import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication(sys.argv)

def _make_tiny_model():
    import tensorflow as tf
    m = tf.keras.Sequential([
        tf.keras.layers.Dense(4, activation="relu", input_shape=(1,)),
        tf.keras.layers.Dense(1),
    ])
    m.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return m

def test_worker_emits_epoch_done(app, qtbot):
    from shared.train_worker import TrainWorker
    x = np.linspace(0, 1, 20).reshape(-1, 1).astype(np.float32)
    y = x * 2
    worker = TrainWorker(_make_tiny_model(), x, y, epochs=3, val_split=0.1)
    epochs_received = []
    worker.epoch_done.connect(lambda ep, logs: epochs_received.append(ep))
    with qtbot.waitSignal(worker.train_done, timeout=30000):
        worker.start()
    assert len(epochs_received) == 3

def test_worker_stop_flag(app, qtbot):
    from shared.train_worker import TrainWorker
    x = np.linspace(0, 1, 50).reshape(-1, 1).astype(np.float32)
    y = x * 2
    worker = TrainWorker(_make_tiny_model(), x, y, epochs=100, val_split=0.1)
    epochs_received = []
    worker.epoch_done.connect(lambda ep, logs: epochs_received.append(ep))
    def stop_early():
        worker.stop()
    QTimer.singleShot(500, stop_early)
    with qtbot.waitSignal(worker.train_done, timeout=15000):
        worker.start()
    assert len(epochs_received) < 100
