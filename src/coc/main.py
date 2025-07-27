from PyQt6.QtWidgets import QApplication
import sys
from coc import Control_pannel 

def main():
    print("hello world")
    app = QApplication(sys.argv)
    panel = Control_pannel.ControlPanel()
    panel.show()
    sys.exit(app.exec())
    