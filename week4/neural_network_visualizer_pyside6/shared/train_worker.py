import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from PySide6.QtCore import QThread, Signal
import numpy as np


class TrainWorker(QThread):
    epoch_done = Signal(int, dict)   # (epoch_index, logs_dict)
    train_done = Signal(object)      # keras History object
    train_error = Signal(str)        # error message string

    def __init__(self, model, x_train, y_train, epochs: int,
                 val_split: float = 0.1, parent=None):
        super().__init__(parent)
        self._model = model
        self._x = x_train
        self._y = y_train
        self._epochs = epochs
        self._val_split = val_split
        self.stop_flag = False

    def run(self):
        import tensorflow as tf

        worker_ref = self

        class _Callback(tf.keras.callbacks.Callback):
            def on_epoch_end(self, epoch, logs=None):
                worker_ref.epoch_done.emit(epoch, dict(logs or {}))
                if worker_ref.stop_flag:
                    self.model.stop_training = True

        try:
            history = self._model.fit(
                self._x, self._y,
                epochs=self._epochs,
                validation_split=self._val_split,
                callbacks=[_Callback()],
                verbose=0,
            )
            self.train_done.emit(history)
        except Exception as exc:
            self.train_error.emit(str(exc))

    def stop(self):
        self.stop_flag = True
