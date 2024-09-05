from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform, QPixmap, QScreen)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QListWidget, QListWidgetItem,
    QMainWindow, QSizePolicy, QVBoxLayout, QWidget, QLabel, QStackedWidget, QComboBox, QTextEdit, QPushButton, QSpacerItem)

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

from qasync import QEventLoop, asyncSlot
import asyncio
from tel.Client import Client
from backend.db import close_session
from ui.page.SendMsgPage import SendMsgPage
from ui.page.DumpMsgPage import DumpMsgPage
from ui.component import Spinner
from util import center, get_conf_path, get_ui_path, get_icon_path
from ui.signal.Signal import Signal, get_global_signal
from ui.component.ApiConfDialog import ApiConfDialog
from ui.component.SignInDialog import SignInDialog

setting_list = ['Message', 'History']

debug = True

class MainPage(object):
    def __init__(self):
        super().__init__()
        ui_file = QFile(get_ui_path("SwitchWindow.ui"))
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        self.setup_signal()
        self.setup_ui(self)
        center(self.window)

        self.window.setWindowTitle('TigiTol')

    async def clean_up(self):
        await Client().disconnect()
        close_session()

    def setup_signal(self):
        self.signal = get_global_signal()
        self.signal.signin_signal.connect(self.on_sign_in)
        self.signal.conf_signal.connect(self.on_conf)

    def setup_ui(self, MainWindow):
        global setting_list

        self.side_bar:QListWidget = self.window.sideBar
        self.stacked_widget:QStackedWidget = self.window.stackedWidget

        self.send_msg_page = SendMsgPage()
        self.dump_msg_page = DumpMsgPage()

        self.stacked_widget.addWidget(self.send_msg_page)
        self.stacked_widget.addWidget(self.dump_msg_page)

        for i in range(len(setting_list)):
            item = QListWidgetItem(self.side_bar)
            # ui_path = 
            side_bar_item = SideBarItem(get_icon_path(f"{setting_list[i].lower()}.svg"), setting_list[i])

            item.setSizeHint(side_bar_item.sizeHint())
            self.side_bar.setItemWidget(item, side_bar_item)

        self.side_bar.setCurrentRow(0)

        self.side_bar.itemClicked.connect(self.switchPage)

    @asyncSlot()
    async def on_conf(self):
        print('on conf')
        self.dialog = ApiConfDialog()
        self.dialog.show()

    @asyncSlot()
    async def on_sign_in(self, client):
        print('on sign_in')
        # self.client = get
        self.dialog = SignInDialog(client)
        self.dialog.show()

    def switchPage(self,item):
        index = self.side_bar.row(item)
        self.stacked_widget.setCurrentIndex(index)

class SideBarItem(QWidget):
    def __init__(self, icon_path, text, icon_size=(35, 35)):
        super().__init__()
        item_layout = QHBoxLayout(self)

        icon_label = QLabel(self)
        pixmap = QPixmap(icon_path)
        scaled_pixmap = pixmap.scaled(icon_size[0], icon_size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(scaled_pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(icon_size[0], icon_size[1])

        label = QLabel(text, self)
        # sub_label = QLabel(text, self)
        info_layout = QVBoxLayout()
        info_layout.addWidget(label)
        # info_layout.addWidget(sub_label)

        item_layout.addWidget(icon_label)
        item_layout.addLayout(info_layout)

        self.setLayout(item_layout)