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
