# tests/test_models.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication(sys.argv)

def test_matplotlib_canvas_creates(app):
    from shared.matplotlib_canvas import MatplotlibCanvas
    c = MatplotlibCanvas()
    assert c.fig is not None
    assert c.ax is not None

def test_matplotlib_canvas_nrows(app):
    from shared.matplotlib_canvas import MatplotlibCanvas
    c = MatplotlibCanvas(nrows=1, ncols=2)
    assert c.axes.shape == (2,)

def test_base_lab_window_raises_without_subclass(app):
    from shared.base_lab_window import BaseLabWindow
    with pytest.raises(NotImplementedError):
        BaseLabWindow("Test")

def test_lab1_make_data_shape():
    from labs.lab1_function.model import make_data
    x_tr, y_tr, x_plot, y_true = make_data("sin(x)")
    assert x_tr.shape == (300, 1)
    assert y_tr.shape == (300, 1)
    assert x_plot.shape == (300,)
    assert y_true.shape == (300,)

def test_lab1_make_model_output_shape():
    from labs.lab1_function.model import make_model
    import numpy as np
    m = make_model([32, 16], "relu", 0.001)
    out = m.predict(np.zeros((5, 1), dtype="float32"), verbose=0)
    assert out.shape == (5, 1)
