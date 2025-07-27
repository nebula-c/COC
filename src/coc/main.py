from PyQt6.QtWidgets import QApplication
import sys
from coc import ControlPanel

def main():
    print("Running...")
    app = QApplication(sys.argv)
    panel = ControlPanel.ControlPanel()
    panel.show()
    sys.exit(app.exec())
    