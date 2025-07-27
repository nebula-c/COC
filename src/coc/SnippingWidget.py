from PyQt6.QtGui import QGuiApplication, QPainter, QPen, QColor, QImage
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, QPoint, QThread, pyqtSignal

import numpy as np
import cv2

from coc import OCRWorker
from coc import OCRLoader

class SnippingWidget(QWidget):
    ocr_done = pyqtSignal(str)
    reader = None  # easyocr.Reader 싱글톤

    def __init__(self, on_close_callback=None):
        super().__init__()
        self.start = QPoint()
        self.end = QPoint()
        self.on_close_callback = on_close_callback

        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        self.setWindowFlags(flags)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self.screen = QGuiApplication.primaryScreen()
        self.full_screenshot = self.screen.grabWindow(0)
        geometry = self.screen.geometry()
        self.setGeometry(geometry)

        self.ocr_thread = None

        if SnippingWidget.reader is None:
            self.ocr_thread = OCRLoader.OCRLoader()
            self.ocr_thread.loaded.connect(self.on_reader_loaded)
            self.ocr_thread.start()
        else:
            self.on_reader_ready(SnippingWidget.reader)

        self.show()

    def on_reader_loaded(self, reader):
        SnippingWidget.reader = reader
        self.on_reader_ready(reader)

    def on_reader_ready(self, reader):
        print("OCR Reader 준비 완료")
        # 이후 OCR 처리 가능

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.red, 2))
        painter.drawPixmap(0, 0, self.full_screenshot)
        if not self.start.isNull() and not self.end.isNull():
            rect = QRect(self.start, self.end).normalized()
            painter.fillRect(rect, QColor(0, 0, 0, 0))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        self.start = event.pos()
        self.end = self.start
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        rect = QRect(self.start, self.end).normalized()
        self.capture_and_ocr(rect)

    def capture_and_ocr(self, rect):
        scale = self.screen.devicePixelRatio()

        x1 = int(rect.left() * scale)
        y1 = int(rect.top() * scale)
        width = int(rect.width() * scale)
        height = int(rect.height() * scale)

        cropped_rect = QRect(x1, y1, width, height)
        cropped = self.full_screenshot.copy(cropped_rect)

        image = cropped.toImage()
        image = image.convertToFormat(QImage.Format.Format_RGBA8888)
        width = image.width()
        height = image.height()
        ptr = image.bits()
        ptr.setsize(image.sizeInBytes())
        arr = np.array(ptr).reshape((height, width, 4))

        rgb_image = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)

        self.ocr_thread = OCRWorker.OCRWorker(rgb_image, SnippingWidget.reader)
        self.ocr_thread.ocr_finished.connect(self.on_ocr_finished)
        self.ocr_thread.ocr_failed.connect(self.on_ocr_failed)
        self.ocr_thread.finished.connect(self.close)
        self.ocr_thread.start()

    def on_ocr_finished(self, results):
        text = '\n'.join([res[1] for res in results]) if results else "[텍스트 없음]"
        self.ocr_done.emit(text)

    def on_ocr_failed(self, error_msg):
        self.ocr_done.emit(f"OCR 실패: {error_msg}")

    def closeEvent(self, event):
        if self.on_close_callback:
            self.on_close_callback()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
