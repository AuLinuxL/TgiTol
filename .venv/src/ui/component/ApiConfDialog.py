# if __name__ == '__main__':
# import sys
# import os
#
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.abspath(os.path.join(current_dir, '../../'))
# sys.path.append(project_root)

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtCore import QFile, Slot
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform, QPixmap, QTextOption)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QListWidget, QListWidgetItem,
                               QMainWindow, QSizePolicy, QVBoxLayout, QWidget, QLabel, QStackedWidget, QComboBox,
                               QTextEdit, QPushButton, QSpacerItem, QAbstractItemView, QLineEdit, QDialog)
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

from backend.db import get_session
from backend.models import Config

from ui.component.MsgBox import warning
from util import get_ui_path

from qasync import QEventLoop, asyncSlot

class ApiConfDialog(QDialog):
    def __init__(self):
        super().__init__()
        ui_file = QFile(get_ui_path("apiConf.ui"))
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.page = loader.load(ui_file)
        ui_file.close()

        layout = QVBoxLayout()
        layout.addWidget(self.page)
        self.setLayout(layout)

        self.setWindowTitle('Api')

        self.session = get_session()
        self.api = self.session.query(Config).first()
        if not self.api:
            print('new')
            self.api = Config()
            print(self.api.id)

        self.setup_ui()

    def setup_ui(self):
        self.apply_btn:QPushButton = self.page.applyBtn
        self.id_input: QLineEdit = self.page.idInput
        self.hash_input: QLineEdit = self.page.hashInput
        self.apply_btn.clicked.connect(self.on_apply)

        # if id := self.api.api_id:
        #     self.id_input.setText(id)
        #
        # if hash := self.api.api_hash:
        #     self.hash_input.setText(hash)

    @asyncSlot()
    async def on_apply(self):
        id = self.id_input.text()
        hash = self.hash_input.text()
        if len(id) != 8 or len(hash) != 32:
            warning(self, "Value Error!")
            return
        self.api.api_id = id
        self.api.api_hash = hash
        if self.api.id != 1:
            self.session.add(self.api)
        self.session.commit()
        from tel.client import Client
        await Client().get()
        self.close()


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    apiConf = ApiConfDialog()
    apiConf.page.show()
    app.exec()