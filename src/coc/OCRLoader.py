from PyQt6.QtCore import QThread, pyqtSignal

import easyocr
import threading

class OCRLoader(QThread):
    loaded = pyqtSignal(object)

    _reader_instance = None
    _reader_lock = threading.Lock()

    def run(self):
        if OCRLoader._reader_instance is None:
            with OCRLoader._reader_lock:
                if OCRLoader._reader_instance is None:
                    OCRLoader._reader_instance = easyocr.Reader(['en', 'ko'], gpu=True)
        
        self.loaded.emit(OCRLoader._reader_instance)
