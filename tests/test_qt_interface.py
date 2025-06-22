import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from interfaces.qt_interface import QtApp


def test_window_title():
    app = QtApp()
    assert app.window.windowTitle() == "The Agency Qt Interface"
