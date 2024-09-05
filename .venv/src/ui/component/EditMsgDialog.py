from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtCore import QFile
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform, QPixmap, QTextOption)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QListWidget, QListWidgetItem,
                               QMainWindow, QSizePolicy, QVBoxLayout,QFormLayout, QWidget, QLabel, QStackedWidget, QComboBox,
                               QTextEdit, QPushButton, QSpacerItem, QAbstractItemView, QLineEdit, QPlainTextEdit, QMessageBox)

from util import get_ui_path, center

import sys
from ui.component.MsgBox import warning

class EditMsgDialog(QMainWindow):
    def __init__(self,signal=None, content=None, delay='5'):
        super().__init__()
        ui_file = QFile(get_ui_path("sendMsgDialog.ui"))
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.page = loader.load(ui_file)
        ui_file.close()

        self.signal = signal
        self.content = content
        self.delay = delay

        # self.isUpdate = true if content else false
        center(self.page)

        self.page.setWindowTitle('Edit msg')
        self.init_ui()

    def init_ui(self):
        self.content_input: QPlainTextEdit = self.page.contentInput
        self.delay_input: QPushButton = self.page.delayInput
        self.save_btn: QPushButton = self.page.saveBtn
        self.cancel_btn: QPushButton = self.page.cancelBtn

        self.save_btn.clicked.connect(self.on_save)
        self.cancel_btn.clicked.connect(self.on_cancel)

        if self.content:
            self.content_input.setPlainText(self.content)

        if int(self.delay) >= 0:
            self.delay_input.setText(self.delay)
        else:
            warning(self,"Delay must large than zero.")

    def on_save(self):
        content = self.content_input.toPlainText()
        delay = self.delay_input.text()

        if int(delay) >= 0 and content != '':
            self.signal.emit_msg_signal(content, delay)
            self.page.close()
        else:
            warning(self,"Value Error!")

    def on_cancel(self):
        print('ok')
        self.page.close()
