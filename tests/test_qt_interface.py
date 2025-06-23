import os
import sys

# Ensure project root is on the import path when running this file directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Allow Qt to run in headless mode during tests
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from interfaces.qt_interface import QtApp


def test_window_title():
    app = QtApp()
    assert app.window.windowTitle() == "The Agency Qt Interface"
