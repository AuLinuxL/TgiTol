from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt, QSignalBlocker)
from PySide6.QtCore import QFile, Slot
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform, QPixmap, QTextOption)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QListWidget, QListWidgetItem,
                               QMainWindow, QSizePolicy, QVBoxLayout, QWidget, QLabel, QStackedWidget, QComboBox,
                               QTextEdit, QPushButton, QSpacerItem, QAbstractItemView)
from PySide6.QtWidgets import QApplication, QMainWindow
from tel.SendMsg import send_msg_by_id, send_msg_by_name
from tel.Client import Client
from qasync import QEventLoop, asyncSlot
from ui.component.EditMsgDialog import EditMsgDialog
from ui.component.SendMsgPageSetting import SendMsgPageSetting

from ui.signal.Signal import Signal

from backend.models import MsgConf
from backend.views import MsgConfView, ConfigView
from backend.db import get_session
from ui.component.HTMLDelegate import HTMLDelegate

from util import get_ui_path, get_icon_path

import asyncio, random
from ui.component.Spinner import Spinner

from enum import Enum

class _MsgConfRole(Enum):
    MSG_ROLE = 100
    DELAY_ROLE = 101

class SendMsgPage(QWidget):
    comboItemName = ['name','id']
    def __init__(self):
        super().__init__()
        ui_file = QFile(get_ui_path("SendMsgPage.ui"))
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.page = loader.load(ui_file)
        ui_file.close()

        layout = QVBoxLayout(self)
        layout.addWidget(self.page)

        self.setup_db()
        self.setup_signal()

        self.setup_ui(self)
        self.spinner = Spinner(self, get_icon_path("static-spinner"), is_static=True)

    def setup_db(self):
        self.session = get_session()
        self.msg_conf_view = MsgConfView(self.session)
        self.conf_view = ConfigView(self.session)
        self.load_setting()
        # msg = MsgConf()
        # msg.content = 'test'
        # msg.delay = '5'
        # self.msg_conf_view.save(msg)

    def load_setting(self):
        conf = self.conf_view.get()
        random = conf.random
        self.is_random = bool(random)
        self.r_from = int(conf.r_from) if conf.r_from else 0
        self.r_to = int(conf.r_to) if conf.r_to else 0

    def setup_signal(self):
        self.signal = Signal()
        self.signal.msg_signal.connect(self.on_msg_received)
        # self.update = {'isUpdate':False,'index':0}
        self.is_update = False
        self.update_row = 0

    def setup_ui(self, Form):
        self.msg_list: QListWidget = self.page.msgList
        self.add_btn: QPushButton = self.page.addBtn
        self.remove_btn: QPushButton = self.page.removeBtn
        self.setting_btn: QPushButton = self.page.settingBtn
        self.mode_combo: QComboBox = self.page.modeCombo
        self.send_btn: QPushButton = self.page.sendBtn
        self.stacked_widget: QStackedWidget = self.page.inputStackedWidget

        # self.msg_list.setEditTriggers(QAbstractItemView.DoubleClicked)
        html_delegate = HTMLDelegate()
        self.msg_list.setItemDelegate(html_delegate)
        self.msg_list.setWordWrap(True)
        self.msg_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.msg_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.msg_list.doubleClicked.connect(self.on_update)
        self.msg_list.itemChanged.connect(self.on_item_change)
        self.msg_list.setSpacing(5)

        msgs = self.msg_conf_view.load()
        for msg in msgs:
            content = msg.content
            delay = msg.delay
            item_content = self.encode_conf(content, delay)
            item = QListWidgetItem(item_content)
            item.setData(_MsgConfRole.DELAY_ROLE.value, delay)
            item.setData(_MsgConfRole.MSG_ROLE.value, content)
            self.msg_list.addItem(item)
            # self.on_msg_received(msg.content,msg.delay)
        self.add_btn.setIcon(QIcon(get_icon_path('add.svg')))
        self.remove_btn.setIcon(QIcon(get_icon_path('minus.svg')))
        self.setting_btn.setIcon(QIcon(get_icon_path('setting.svg')))

        name_input_group = NameInput()
        self.name_input = name_input_group.name_input
        self.stacked_widget.addWidget(name_input_group)
        self.setup_state(Form)

        id_input_group = IdInput()
        self.id_input = id_input_group.id_input
        self.group_input = id_input_group.group_input
        self.stacked_widget.addWidget(id_input_group)
        self.stacked_widget.setCurrentIndex(0)
        # self.stacked_widget.setCurrentWidget(idInput)
        # self.on_index_changed(0)

    def setup_state(self, Form):
        # Form.setWindowTitle(QCoreApplication.translate("Form", u"Name", None))
        self.mode_combo.addItem(self.comboItemName[0])
        self.mode_combo.addItem(self.comboItemName[1])
        # self.mode_combo.setItemText(0, QCoreApplication.translate("Form", self.comboItemName[0], None))
        # self.mode_combo.setItemText(1, QCoreApplication.translate("Form", self.comboItemName[1], None))

        self.mode_combo.currentIndexChanged.connect(self.on_index_changed)
        self.on_index_changed(0)

        self.send_btn.setText(QCoreApplication.translate("Form", u"Send", None))

        self.send_btn.clicked.connect(self.on_send)
        self.add_btn.clicked.connect(self.on_add)
        self.remove_btn.clicked.connect(self.on_remove)
        self.setting_btn.clicked.connect(self.on_setting)

        start = self.msg_list.indexAt(QPoint()).row()
        end = self.msg_list.indexAt(self.msg_list.viewport().rect().bottomRight()).row()
        print('start',start)
        print('end', end)

    @Slot(str,str)
    def on_msg_received(self,content,delay):
        item_content = self.encode_conf(content,delay)
        item = QListWidgetItem(item_content)
        item.setData(_MsgConfRole.DELAY_ROLE.value, delay)
        item.setData(_MsgConfRole.MSG_ROLE.value, content)
        if not self.is_update:
            self.msg_list.addItem(item)
            self.msg_conf_view.save(content=content,delay=delay)
        else:
            index = self.update_row
            print('update index',index)
            item = self.msg_list.item(index)
            item.setText(item_content)
            obj = self.msg_conf_view.query(index + 1)
            self.msg_conf_view.update(obj,content,delay)
            self.is_update = False

    def encode_conf(self,content, delay):
        content = content.replace('\n', '<br/>')
        return f"<span style='color: grey;'>content</span>:<div style='margin-left: 15px; margin-top: 10px;'>{content}</div><br/><span style='color: grey;'>delay:{delay}</span>"

    def get_data(self, item):
        content = item.data(_MsgConfRole.MSG_ROLE.value)
        delay = item.data(_MsgConfRole.DELAY_ROLE.value)
        return content, delay

    def on_update(self,index):
        row = index.row()
        print('update_row',row)
        item = self.msg_list.item(row)
        self.is_update = True
        self.update_row = row
        content, delay = self.get_data(item)
        self.dialog = EditMsgDialog(signal=self.signal,content=content,delay=delay)
        self.dialog.page.show()

    def on_index_changed(self,index):
        match (index):
            case 0:
                self.stacked_widget.setCurrentIndex(0)
            case 1:
                self.stacked_widget.setCurrentIndex(1)

    def on_setting(self):
        dialog = SendMsgPageSetting()
        dialog.page.show()
        dialog.exec()

    def on_add(self):
        self.dialog = EditMsgDialog(signal=self.signal)
        self.dialog.page.show()

    def on_remove(self):
        for item in self.msg_list.selectedItems():
            index = self.msg_list.row(item)
            print(index)
            obj = self.msg_conf_view.query(index + 1)
            self.msg_conf_view.delete(obj)
        for item in self.msg_list.selectedItems():
            index = self.msg_list.row(item)
            self.msg_list.takeItem(index)
        objs = self.session.query(MsgConf).all()
        num = len(objs)
        for o in range(num):
            obj = objs[o]
            obj.id = o + 1
        self.session.commit()

    @asyncSlot()
    async def on_send(self):
        self.spinner.start()
        try:
            self.load_setting()
            self.send_btn.setDisabled(True)
            msg_list = []
            for i in range(self.msg_list.count()):
                item = self.msg_list.item(i)
                if self.is_random:
                    content = self.msg_list.data(_MsgConfRole.MSG_ROLE.value)
                    delay = random.randint(self.r_from, self.r_to)
                    print(delay)
                else:
                    content, delay = self.get_data(item)
                msg = {'msg':content,'delay':delay}
                msg_list.append(msg)
            mode = self.comboItemName[self.mode_combo.currentIndex()]
            print(mode)
            self.client = await Client().get()
            if mode == "id":
                group_id = int(self.group_input.toPlainText())
                user_id = int(self.id_input.toPlainText())
                await send_msg_by_id(self.client, msg_list, target_id=user_id, group_id=group_id)
            elif mode == "name":
                user_name = self.name_input.toPlainText()
                print(user_name)
                await send_msg_by_name(self.client, msg_list, target_name=user_name)
            self.send_btn.setDisabled(False)
        finally:
            self.spinner.delete()


    def on_item_change(self,item):
        print(f"Item changed: {item.text()}")

class IdInput(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)
        # self.layout.addWidget(self.layout)
        self.setup_db()
        self.setup_ui()

    def setup_db(self):
        self.session = get_session()
        self.conf_view = ConfigView(self.session)
        self.conf = self.conf_view.get()

    def setup_ui(self):
        self.group_lable = QLabel(self)
        self.group_lable.setObjectName(u"groupLable")

        self.layout.addWidget(self.group_lable)

        self.group_input = QTextEdit(self)
        self.group_input.setObjectName(u"groupInput")
        self.group_input.setMaximumSize(QSize(16777215, 24))
        self.group_input.setWordWrapMode(QTextOption.NoWrap)
        self.group_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.group_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.group_input.setFontPointSize(12)

        self.layout.addWidget(self.group_input)

        self.id_lable = QLabel(self)
        self.id_lable.setObjectName(u"idLable")

        self.layout.addWidget(self.id_lable)

        self.id_input = QTextEdit(self)
        self.id_input.setObjectName(u"idInput")
        self.id_input.setMaximumSize(QSize(16777215, 24))
        self.id_input.setWordWrapMode(QTextOption.NoWrap)
        self.id_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.id_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.id_input.setFontPointSize(12)

        self.layout.addWidget(self.id_input)

        id_content = self.conf.usr_id
        group_content = self.conf.group_id

        self.id_input.setText(id_content)
        self.group_input.setText(group_content)
        self.id_input.textChanged.connect(self.on_id_change)
        self.group_input.textChanged.connect(self.on_group_change)

        self.group_lable.setText("Group")
        self.id_lable.setText("Id")

    def on_id_change(self):
        content = self.id_input.toPlainText()
        self.conf_view.save(usr_id = content)

    def on_group_change(self):
        content = self.group_input.toPlainText()
        self.conf_view.save(group_id = content)

class NameInput(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)
        # self.layout.addWidget(self.layout)
        self.setup_db()
        self.setup_ui()

    def setup_db(self):
        self.session = get_session()
        self.conf_view = ConfigView(self.session)
        self.conf = self.conf_view.get()

    def setup_ui(self):
        self.name_lable = QLabel(self)
        self.name_lable.setObjectName(u"nameLable")
        self.layout.addWidget(self.name_lable)

        self.name_input = QTextEdit(self)
        self.name_input.setObjectName(u"nameInput")
        self.name_input.setMaximumSize(QSize(16777215, 24))
        self.name_input.setWordWrapMode(QTextOption.NoWrap)
        self.name_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.name_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.name_input.setFontPointSize(12)
        name_content = self.conf.usr_name
        self.name_input.setText(name_content)
        self.layout.addWidget(self.name_input)
        self.name_input.textChanged.connect(self.on_text_change)

        self.name_lable.setText(QCoreApplication.translate("Form", u"Name", None))

    def on_text_change(self):
        content = self.name_input.toPlainText()
        self.conf_view.save(usr_name=content)

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    IdEditor = SendMsgPage()
    IdEditor.show()
    app.exec()
