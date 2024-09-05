from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform, QPixmap, QScreen)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QListWidget, QListWidgetItem,
    QMainWindow, QSizePolicy, QVBoxLayout, QWidget, QLabel, QStackedWidget, QComboBox, QTextEdit, QPushButton, QCheckBox, QLineEdit, QDialog)

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from backend.views import ConfigView
from backend.db import get_session
from util import get_ui_path, center

class SendMsgPageSetting(QDialog):
    comboItemName = ['name','id']
    def __init__(self):
        super().__init__()
        ui_file = QFile(get_ui_path("SendMsgPageSetting.ui"))
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.page = loader.load(ui_file)
        ui_file.close()

        layout = QVBoxLayout()
        layout.addWidget(self.page)
        self.setLayout(layout)

        # self.center(self.page)

        self.setWindowTitle('Setting')

        self.setup_db()

        self.setup_ui()

        center(self.page)

    def setup_db(self):
        self.session = get_session()
        self.conf_view = ConfigView(self.session)
        self.conf = self.conf_view.get()

    def setup_ui(self):
        self.random_cb: QCheckBox = self.page.randomCb
        self.apply_btn: QPushButton = self.page.applyBtn
        self.from_input: QLineEdit = self.page.fromInput
        self.to_input: QLineEdit = self.page.toInput

        r_from = self.conf.r_from
        self.from_input.setText(r_from)
        r_to = self.conf.r_to
        self.to_input.setText(r_to)
        random = self.conf.random
        self.random_cb.setChecked(bool(random))

        self.apply_btn.clicked.connect(self.on_apply)

    def on_apply(self):
        r_from = self.from_input.text()
        r_to = self.to_input.text()
        random = self.random_cb.isChecked()
        conf = self.conf_view.save(random=random,r_from=r_from,r_to=r_to)
        self.session.commit()
        self.close()




