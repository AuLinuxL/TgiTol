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
from backend.db import get_session
from backend.models import Channel, Group

from qasync import asyncSlot, asyncClose
from util import get_ui_path, center
from tel.SyncEntity import get_entity_list

import asyncio

class PickEntityDialog(QDialog):
    def __init__(self, signal):
        super().__init__()
        ui_file = QFile(get_ui_path("PickEntityDialog.ui"))
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.page = loader.load(ui_file)
        ui_file.close()

        layout = QVBoxLayout()
        layout.addWidget(self.page)
        self.setLayout(layout)

        # self.center(self.page)
        self.setWindowTitle('Setting')
        self.resize(350,400)
        # self.initEntity()
        center(self.page)
        self.signal = signal
        self.setup_ui()

        asyncio.ensure_future(self.async_init())

    async def async_init(self):
        session = get_session()
        self.channel_list,self.group_list = await get_entity_list(session)
        self.update_list()

    def setup_ui(self):
        self.choose_btn: QPushButton = self.page.chooseBtn
        self.update_btn: QPushButton = self.page.updateBtn
        self.entity_list: QListWidget = self.page.entityList

        print('bind')
        self.choose_btn.clicked.connect(self.on_choose)
        self.update_btn.clicked.connect(self.on_update)
    # @asyncClose
    # async def async_exec(self):
    #     return await asyncio.get_event_loop().run_in_executor(None, self.exec_)
    def update_list(self):
        self.entity_list.clear()
        print('self.channel_list',self.channel_list)
        for channel in self.channel_list:
            item = QListWidgetItem(channel.channel_name)
            channel_id = '-100' + str(channel.channel_id)
            item.setData(Qt.UserRole,channel_id)
            self.entity_list.addItem(item)
        for group in self.group_list:
            item = QListWidgetItem(group.group_name)
            group_id = '-100' + str(group.group_id)
            item.setData(Qt.UserRole, group_id)
            self.entity_list.addItem(item)
            # self.close()

    @asyncSlot()
    async def on_update(self):
        session = get_session()
        self.channel_list,self.group_list = await get_entity_list(session, is_update = True)
        self.update_list()

    def on_choose(self):
        item = self.entity_list.selectedItems()
        if item:
            item = item[0]
            self.entity_list.row(item)
            print(item.data(Qt.UserRole))
            self.signal.emit_pick_entity_signal(item.data(Qt.UserRole))
            self.close()
        # print(item.data(Qt.UserRole))

    # def updateEntityList(self):