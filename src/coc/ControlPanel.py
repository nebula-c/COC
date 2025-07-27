from PyQt6.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout, QLabel
from coc import SnippingWidget

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR 리모콘")
        self.setFixedSize(300, 300)

        self.start_btn = QPushButton("캡처 시작", self)
        self.start_btn.clicked.connect(self.start_capture)

        self.status_label = QLabel("", self)
        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.start_btn)
        layout.addWidget(self.status_label)
        layout.addWidget(self.result_text)
        self.setLayout(layout)

        self.snip_window = None

    def start_capture(self):
        # self.hide()
        self.status_label.setText("")
        self.result_text.clear()
        self.snip_window = SnippingWidget.SnippingWidget(on_close_callback=self.on_snip_closed)
        self.snip_window.ocr_done.connect(self.on_ocr_done)
        self.snip_window.show()

    def on_snip_closed(self):
        self.show()
        if not self.result_text.toPlainText():
            self.status_label.setText("캡처 취소됨")

    def on_ocr_done(self, text):
        self.result_text.setPlainText(text)
        self.status_label.setText("캡처 완료")
