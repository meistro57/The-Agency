from PyQt6 import QtWidgets, QtCore
import sys
from main import run_agency
import builtins

class QtApp:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = QtWidgets.QWidget()
        self.window.setWindowTitle("The Agency Qt Interface")
        self.layout = QtWidgets.QVBoxLayout()
        self.prompt_edit = QtWidgets.QTextEdit()
        self.prompt_edit.setPlaceholderText("Describe the project you want built...")
        self.run_button = QtWidgets.QPushButton("Run")
        self.output_area = QtWidgets.QTextEdit()
        self.output_area.setReadOnly(True)
        self.layout.addWidget(self.prompt_edit)
        self.layout.addWidget(self.run_button)
        self.layout.addWidget(self.output_area)
        self.window.setLayout(self.layout)
        self.run_button.clicked.connect(self.handle_run)

    def handle_run(self):
        prompt = self.prompt_edit.toPlainText().strip()
        if not prompt:
            QtWidgets.QMessageBox.warning(self.window, "Input Required", "Please enter a prompt.")
            return
        self.output_area.append(f"Running: {prompt}")
        orig_input = builtins.input
        builtins.input = lambda _='': 'no'
        try:
            run_agency(prompt)
            self.output_area.append("Finished")
        finally:
            builtins.input = orig_input

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    QtApp().run()
