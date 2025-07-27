from PyQt6.QtCore import QThread, pyqtSignal

class OCRWorker(QThread):
    ocr_finished = pyqtSignal(list)
    ocr_failed = pyqtSignal(str)

    def __init__(self, image_np, reader):
        super().__init__()
        self.image_np = image_np
        self.reader = reader

    def run(self):
        try:
            results = self.reader.readtext(self.image_np)
            self.ocr_finished.emit(results)
        except Exception as e:
            self.ocr_failed.emit(str(e))
