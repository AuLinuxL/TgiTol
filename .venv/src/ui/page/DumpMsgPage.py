import asyncio, os, time, subprocess

import ujson
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt, QSignalBlocker)
from PySide6.QtCore import QFile, Slot
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform, QPixmap, QTextOption, QAction)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QListWidget, QListWidgetItem,
                               QMainWindow, QSizePolicy, QVBoxLayout, QWidget, QLabel, QStackedWidget, QComboBox,
                               QTextEdit, QPushButton, QSpacerItem, QAbstractItemView, QLineEdit, QMenu, QMessageBox)
from PySide6.QtWidgets import QApplication, QMainWindow
from tel.Client import Client
from qasync import asyncSlot
from ui.component.SendMsgPageSetting import SendMsgPageSetting
from ui.component.PickEntityDialog import PickEntityDialog
from ui.component.DumpSettingDialog import DumpSettingDialog
from ui.component.DetailDialog import DetailDialog
from ui.component.HTMLDelegate import HTMLDelegate
from backend.models import Channel, Group
from backend.views import ProfileView, get_username

from tel.DumpMsg import DumpMsg
from util import get_input_entity_id

from ui.signal.Signal import Signal
from ui.component.Spinner import Spinner

from backend.db import get_session
from backend.views import ConfigView, MessageView

from util import trigger_show_layout, get_ui_path, get_icon_path
from ui.component.MsgBox import warning
import threading
from telethon.tl.types import PeerChannel

from datetime import datetime, timedelta
import pytz, tzlocal
from enum import Enum

COMBO_ITEM = ('Msg', 'Name', 'UName', 'UId')
class _MsgRole(Enum):
    PK_ROLE = 1
    PROFILE_ID_ROLE = 100
    MSG_ID_ROLE = 200
    FWD_ENTITY_ID_ROLE = 300
    CHANNEL_NAME_ROLE = 301
    IS_USER_ROLE = 302

class DumpMsgPage(QWidget):
    SELF_ID = 100

    def __init__(self):
        global COMBO_ITEM
        super().__init__()
        ui_file = QFile(get_ui_path("DumpMsgPage.ui"))
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.page = loader.load(ui_file)
        ui_file.close()

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.page)

        self.on_search = False
        self.isUpdated = False

        self.combo_item = COMBO_ITEM
        self.search_mode = self.combo_item[0]

        self.page_count = 2
        self.split_interval = 2500

        self.spinner = Spinner(self, get_icon_path("static-spinner"), is_static=True)
        self.spinner.hide()

        self.split_keyword = None
        self.dump_self = False

        self.setup_signal()
        self.setup_db()
        self.setup_ui()

    def setup_signal(self):
        self.signal = Signal()
        self.signal.pick_entity_signal.connect(self.on_pick)
        self.signal.msg_list_signal.connect(self.on_msg_return)

    def setup_db(self):
        self.session = get_session()
        self.conf_view = ConfigView(self.session)
        self.conf = self.conf_view.get()
        self.msg_view = MessageView(self.session)
        self.pro_view = ProfileView(self.session)

    def setup_ui(self):
        self.dump_btn: QListWidget = self.page.dumpBtn
        self.choose_btn: QPushButton = self.page.chooseBtn
        self.show_search_btn: QPushButton = self.page.showSearchBtn
        self.search_btn: QPushButton = self.page.searchBtn
        self.msg_view_list: QListWidget = self.page.msgViewList
        self.profile_list: QListWidget = self.page.profileList
        self.entity_input: QLineEdit = self.page.entityInput
        self.search_input: QLineEdit = self.page.searchInput
        self.search_layout: QHBoxLayout = self.page.searchLayout
        self.entity_layout: QHBoxLayout = self.page.entityLayout
        self.split_layout: QHBoxLayout = self.page.splitLayout
        self.mode_combo: QComboBox = self.page.modeCombo
        self.split_list: QListWidget = self.page.splitList
        self.dump_offset_btn: QPushButton = self.page.dumpOffsetBtn

        self.search_btn.hide()
        self.split_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.split_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.split_list.setFlow(QListWidget.Flow.LeftToRight)

        self.split_list.horizontalScrollBar().setStyleSheet(
            """
            QScrollBar:horizontal {
               height: 5px;
               background: rgba(240, 240, 240, 0);
               border: 1px solid rgba(240, 240, 240, 0);
               border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
               background: rgba(176, 176, 176, 65);
               border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
               background: rgba(240, 240, 240, 0);
               border: 0px solid rgba(240, 240, 240, 0);
               border-radius: 5px;
            }
            """
        )

        # set not to preload all items to plan the scroll bar size and position
        # self.msg_view_list.setUniformItemSizes(True)

        html_delegate = HTMLDelegate()
        self.msg_view_list.setItemDelegate(html_delegate)
        self.msg_view_list.setWordWrap(True)
        self.msg_view_list.setSpacing(5)

        # self.msg_view_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        # self.msg_view_list.setFlow(QListWidget.Flow.LeftToRight)

        # Get spacer
        for i in range(self.search_layout.count()):
            item = self.search_layout.itemAt(i)
            if isinstance(item,QSpacerItem):
                print('find',item)
                self.spacer: QSpacerItem = item

        for i in self.combo_item:
            self.mode_combo.addItem(i)

        self.mode_combo.currentIndexChanged.connect(self.on_search_mode)

        self.update_profile_list()

        self.profile_list.doubleClicked.connect(self.on_profile)
        self.msg_view_list.doubleClicked.connect(self.on_jump)
        self.msg_view_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.msg_view_list.customContextMenuRequested.connect(self.on_right_click)

        self.entity_input.setText(self.conf.his_entity)
        self.search_input.setText(self.conf.his_search)

        self.entity_input.textChanged.connect(self.on_entity_change)
        self.search_input.textChanged.connect(self.on_search_change)

        trigger_show_layout(self.search_layout,False)
        trigger_show_layout(self.split_layout,False)
        self.show_search_btn.clicked.connect(self.on_show_search)

        self.search_btn.clicked.connect(self.on_search_clicked)
        self.choose_btn.clicked.connect(self.on_choose)

        # self.msg_list.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.profile_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.msg_view_list.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.choose_btn.setIcon(QIcon(get_icon_path("list.svg")))
        self.show_search_btn.setIcon(QIcon(get_icon_path("search.svg")))

        self.dump_btn.clicked.connect(self.on_dump)
        # self.dump_offset_btn.clicked.connect(self.on_dump_setting)
        self.dump_offset_btn.clicked.connect(lambda _:self.on_dump_offset())

        self.profile_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.profile_list.customContextMenuRequested.connect(self.show_context_menu)

    def on_right_click(self, index):
        print('on_right_click')
        item = self.msg_view_list.itemAt(index)
        if item:
            pk = item.data(_MsgRole.PK_ROLE.value)
            msg = self.msg_view.get_by_pk(pk)
            # if msg:
            # print('pk', pk)
            self.dialog = DetailDialog(msg)
            self.dialog.show()

    def on_search_mode(self, index):
        match (index):
            case 0:
                self.search_mode = self.combo_item[0]
            case 1:
                self.search_mode = self.combo_item[1]
            case 2:
                self.search_mode = self.combo_item[2]
            case 3:
                self.search_mode = self.combo_item[3]

    def show_context_menu(self, index):
        item = self.profile_list.itemAt(index)
        if item:
            menu = QMenu(self)

            update_action = QAction('Update', self)
            delete_action = QAction('Delete', self)

            update_action.triggered.connect(lambda: self.update_item(item))
            delete_action.triggered.connect(lambda: self.delete_item(item))

            menu.addAction(update_action)
            menu.addAction(delete_action)

            profile_id = item.data(_MsgRole.PROFILE_ID_ROLE.value)
            if profile_id and int(profile_id) == self.SELF_ID:
                rec_action = QAction('Recover', self)
                rec_action.triggered.connect(lambda: self.rec_saved(item))
                menu.addAction(rec_action)

            menu.exec_(self.profile_list.mapToGlobal(index))

    @asyncSlot()
    async def rec_saved(self, item):
        async def forward_msg(fwd_entity_id,msg_id):
            entity = 'me'
            from_peer = PeerChannel(channel_id=fwd_entity_id)
            await self.client.forward_messages(entity, msg_id, from_peer)

        def pre_gfwd(grouped_msgs):
            fwd_entity_id = None
            msg_id = []
            for gmsg in grouped_msgs:
                ginfo = self.msg_view.get_fwd_info(gmsg.forward_info)
                if gmsg == grouped_msgs[0]:
                    fwd_entity_id = ginfo.fwd_entity_id
                msg_id.append(ginfo.fwd_msg_id)
            return fwd_entity_id, msg_id

        def pre_sfwd(msg):
            fwd_info = self.msg_view.get_fwd_info(msg.forward_info)
            fwd_entity_id = fwd_info.fwd_entity_id
            msg_id = fwd_info.fwd_msg_id
            return fwd_entity_id, msg_id

        async def single_fwd(msg):
            fwd_entity_id, msg_id = pre_sfwd(msg)
            await forward_msg(fwd_entity_id, msg_id)

        async def grouped_fwd(grouped_msgs):
            fwd_entity_id, msg_id = pre_gfwd(grouped_msgs)
            await forward_msg(fwd_entity_id, msg_id)

        self.spinner.start()
        if not hasattr(self, 'client'):
            self.client = await Client().get()
        total, msg_list = self.msg_view.get_all(self.SELF_ID)
        grouped_msgs = []
        current_gid = None
        for msg in msg_list:

            print('-----------------------------------------------------------------------------------------------')
            print(msg)
            print('-----------------------------------------------------------------------------------------------')

            # if hasattr(msg, 'forward_info'):
            if msg.forward_info:
                fwd_info = self.msg_view.get_fwd_info(msg.forward_info)
                grouped_id = msg.grouped_id
                if grouped_id:
                    if not current_gid:
                        current_gid = grouped_id
                        grouped_msgs.append(msg)
                    elif current_gid == grouped_id:
                        grouped_msgs.append(msg)
                    elif current_gid and current_gid != grouped_id:
                        # Fwd
                        await grouped_fwd(grouped_msgs)
                        grouped_msgs = []
                        current_gid = grouped_id
                        grouped_msgs.append(msg)
                else:
                    if current_gid:
                        # Fwd
                        await grouped_fwd(grouped_msgs)
                        grouped_msgs = []
                        current_gid = None
                        # Fwd single
                        await single_fwd(msg)
                    else:
                        # Fwd single
                        await single_fwd(msg)
            else:
                if message := msg.message:
                    await self.client.send_message('me', message)
                continue
        self.spinner.delete()
        print('finished')

    @asyncSlot()
    async def update_item(self, item):
        self.spinner.start()
        self.ex_id = item.data(_MsgRole.PROFILE_ID_ROLE.value)
        start_id = self.msg_view.get_max_entity_id(self.ex_id)
        print(start_id)
        # exit()
        self.client = await Client().get()
        entity = await self.client.get_input_entity(self.ex_id)
        print(start_id)
        dump = DumpMsg(self.client, entity, self.signal, start_id = start_id )
        await dump.dump_msg()
        self.read_db(self.msg_view, self.signal, self.ex_id)

    def delete_item(self, item):
        id = item.data(_MsgRole.PROFILE_ID_ROLE.value)
        self.msg_view.delete(id)
        self.pro_view.delete(id)
        self.profile_list.takeItem(self.profile_list.row(item))

    def update_profile_list(self):
        self.profile_list.clear()
        proList = self.pro_view.get()
        for pro in proList:
            item = QListWidgetItem(pro.name)
            print(pro.entity_id)
            item.setData(_MsgRole.PROFILE_ID_ROLE.value,pro.entity_id)
            self.profile_list.addItem(item)

    def trigger_search_layout(self,is_show):
        if is_show:
            self.spacer.changeSize(0, 0, QSizePolicy.Fixed, QSizePolicy.Fixed)
            trigger_show_layout(self.search_layout, True)
            trigger_show_layout(self.entity_layout,False)
            self.dump_btn.hide()
            self.dump_offset_btn.hide()
            self.search_btn.show()
        else:
            self.spacer.changeSize(0, 0, QSizePolicy.Expanding, QSizePolicy.Preferred)
            trigger_show_layout(self.search_layout, False)
            trigger_show_layout(self.entity_layout,True)
            self.dump_btn.show()
            self.dump_offset_btn.show()
            self.search_btn.hide()

    # def on_dump_setting(self):
        # self.dialog = DumpSettingDialog()
        # self.dialog.show()

    # def on_dump_offset(self, dateInterval=2):
    #     DumpMsg()

    def on_dump_offset(self, dateInterval=2):
        localtz = tzlocal.get_localzone()
        if localtz:
            tz = localtz
        else:
            tz = pytz.utc
        end_date = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=dateInterval)
        end_date = end_date + timedelta(days=1)
        print('start',start_date)
        print('end',end_date)
        self.on_dump(start_date=start_date, end_date=end_date)

    @asyncSlot()
    async def on_jump(self,index):
        row = index.row()
        item = self.msg_view_list.item(row)
        fwd_entity_id = item.data(_MsgRole.FWD_ENTITY_ID_ROLE.value)
        channel_name = item.data(_MsgRole.CHANNEL_NAME_ROLE.value)
        is_user = int(item.data(_MsgRole.IS_USER_ROLE.value) if item.data(_MsgRole.IS_USER_ROLE.value) else 0)
        if is_user:
            print('Message is private!')
            return
        print('fwd_entity_id',fwd_entity_id,'channel_name',channel_name)
        message_id = item.data(_MsgRole.MSG_ID_ROLE.value)
        if fwd_entity_id or channel_name:
            if channel_name:
                jump_url = f'tg://resolve?domain={channel_name}&post={message_id}'
            else:
                jump_url = f'tg://privatepost?channel={fwd_entity_id}&post={message_id}'
        else:
            is_private, username = get_username(self.session, self.ex_id)
            if not username:
                self.client = await Client().get()
                try:
                    entity = await self.client.get_entity(int(self.ex_id))
                except ValueError as e:
                    print(e)
                    return
                try:
                    username = entity.username
                except Exception as e:
                    print(e)
                    is_private = True
            if is_private:
                jump_url = f'tg://privatepost?channel={self.ex_id}&post={message_id}'
            else:
                jump_url = f'tg://resolve?domain={username}&post={message_id}'

        print(jump_url)
        subprocess.run(['xdg-open',jump_url])

    def on_profile(self,index):
        # self.spinner.start()
        row = index.row()
        item = self.profile_list.item(row)
        entity_id = item.data(_MsgRole.PROFILE_ID_ROLE.value)
        self.ex_id, _ = self.msg_view.exist(str(entity_id))
        self.page_count = 0
        self.read_db(self.msg_view, self.signal, entity_id)

    def on_pick(self,id):
        if(id):
            self.entity_input.setText(id)
        else:
            print('Wrong id!')

    def on_entity_change(self):
        entity = self.entity_input.text()
        self.conf_view.save(his_entity = entity)

    def on_search_change(self):
        search = self.search_input.text()
        self.conf_view.save(his_search = search)

    def on_choose(self):
        # if not self.isUpdated:
        # channelList,groupList = await getEntityList(self.session, isUpdate = not self.isUpdated)
        # channelList,groupList = await getEntityList(self.session)
        # print('grouplist',groupList)
        # self.isUpdated = True
        self.dialog = PickEntityDialog(self.signal)
        self.dialog.show()
        # dialog = PickEntityDialog(channelList, groupList)
        # result = await dialog.async_exec()
        # if result == QDialog.Accepted:
        #     selected_item = dialog.get_selected_item()
        #     print(f"Selected: {selected_item}")

    def on_search_clicked(self):
        # self.spinner.start()
        self.page_count = 0
        if not self.ex_id:
            warning(self,'Entity not set!')
        else:
            keyword = self.search_input.text()
            if self.search_mode == self.combo_item[0]:
                self.read_db(self.msg_view, self.signal, self.ex_id, keyword=keyword, search_mode=self.search_mode)
            elif self.search_mode == self.combo_item[1]:
                self.read_db(self.msg_view, self.signal, self.ex_id, keyword=keyword, search_mode=self.search_mode, is_usr_name=False)
            elif self.search_mode == self.combo_item[2]:
                self.read_db(self.msg_view, self.signal, self.ex_id, keyword=keyword, search_mode=self.search_mode, is_usr_name=True)
            elif self.search_mode == self.combo_item[3]:
                self.read_db(self.msg_view, self.signal, self.ex_id, keyword=keyword, search_mode=self.search_mode)

    def on_show_search(self):
        if not self.on_search:
            print('search')
            self.on_search = True
            self.trigger_search_layout(True)
        else:
            self.on_search = False
            self.trigger_search_layout(False)

    def on_splite(self):
        btn = self.sender()
        print('btn.text()',btn.text())
        self.page_count = int(btn.text()) - 1
        print('self.page_count',self.page_count)
        if self.split_keyword:
            self.read_db(self.msg_view, self.signal, self.ex_id, keyword=self.split_keyword, search_mode=self.search_mode)
        else:
            self.read_db(self.msg_view, self.signal, int(self.ex_id))

    def split_page(self,total):
        print("total",total)
        trigger_show_layout(self.split_layout,True)
        self.split_list.clear()
        if total > self.split_interval:
            page_count = (total // self.split_interval) + 1
            for p in range(page_count):
                p = p + 1
                btn = QPushButton(str(p))
                btn.clicked.connect(self.on_splite)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                btn.setStyleSheet(
                    """padding: 5px 10px;
                    margin-left: 5px;
                    margin-right: 5px;
                    margin-bottom: 1px;
                    font-size: 11px;
                    border: 1px solid #ccc;
                    border-radius: 5px; """
                    # "background-color: #f0f0f0;"
                )
                btn.adjustSize()
                btn.setFixedHeight(22)
                item = QListWidgetItem()
                item.setSizeHint(QSize(btn.sizeHint().width(),btn.sizeHint().height()))
                self.split_list.addItem(item)
                self.split_list.setItemWidget(item,btn)
        else:
            trigger_show_layout(self.split_layout, False)

    def on_msg_return(self,msg_list, total, is_start, keyword):
        self.split_keyword = keyword
        # if total > self.split_interval:
        self.split_page(total)
        print('Msg return')
        if is_start:
            self.msg_view_list.clear()
        # print(len(msgs_list))
        msg_list.reverse()
        for msg in msg_list:
            # print('-----------------------------------------------------------------------------------------------')
            # print(msg)
            # print('-----------------------------------------------------------------------------------------------')
            # get_usr_name
            usr_name = self.msg_view.get_sender_name(msg.sender_id)
            # message_content = msg.message
            if keyword:
                lower_keyword = keyword.lower()
                if self.search_mode == self.combo_item[0]:
                    content = msg.message
                    lower_msg = content.lower()
                    index = lower_msg.find(lower_keyword)

                    if index != -1:
                        before_keyword = content[:index]
                        after_keyword = content[index + len(keyword):]
                        light_keyword = content[index:index + len(keyword)]
                        message_content = f"{before_keyword}<span style='color: red;'>{light_keyword}</span>&nbsp;&nbsp;{after_keyword}"
                    else:
                        message_content = content

                elif self.search_mode == self.combo_item[1]:
                    lower_name = usr_name.lower()
                    index = lower_name.find(lower_keyword)

                    if index != -1:
                        before_keyword = usr_name[:index]
                        after_keyword = usr_name[index + len(keyword):]
                        light_keyword = usr_name[index:index + len(keyword)]
                        usr_name = f"{before_keyword}<span style='color: red;'>{light_keyword}</span>{after_keyword}"
                    else:
                        usr_name = usr_name

                    message_content = msg.message

                else:
                    message_content = msg.message
            else:
                message_content = msg.message

            if message_content:
                message_content = message_content.replace('\n', '<br/>')

            # print('message_content',message_content)
            if usr_name:
                content = f"<span style='color: grey; font-size:13px;'>{usr_name}</span>:<div style='margin-left: 15px; margin-top: 10px;'>{message_content}</div>"
            else:
                content = message_content
            if message_content:
                item = QListWidgetItem(content)
                item.setData(_MsgRole.PK_ROLE.value, msg.id)
                if not msg.forward_info:
                    item.setData(_MsgRole.MSG_ID_ROLE.value, msg.message_id)
                    self.msg_view_list.addItem(item)
                elif msg.forward_info:
                    fwd_info = self.msg_view.get_fwd_info(msg.forward_info)
                    if fwd_info:
                        item.setData(_MsgRole.MSG_ID_ROLE.value, fwd_info.fwd_msg_id)
                        item.setData(_MsgRole.FWD_ENTITY_ID_ROLE.value, fwd_info.fwd_entity_id)
                        item.setData(_MsgRole.CHANNEL_NAME_ROLE.value, fwd_info.channel_name)
                        item.setData(_MsgRole.IS_USER_ROLE.value, fwd_info.is_user)
                    self.msg_view_list.addItem(item)
        self.spinner.delete()
        # print('on_msg_return', msg_list)

    def read_db(self,msgView , signal, entity_id, search_mode = None, keyword = None, is_usr_name = False):
        # self.page_count = 0
        self.thread = None
        entity_id = int(entity_id)
        self.thread = ReadDbThread(msgView, signal, entity_id, split_count=self.page_count, split_interval=self.split_interval, search_mode = search_mode, keyword=keyword, is_usr_name=is_usr_name)
        self.thread.start()

    @asyncSlot()
    async def on_dump(self, start_date = None, end_date = None):
        self.spinner.start()
        # self.layout.addWidget(self.spinner)
        # self.spinner.center(self)
        self.dump_btn.setDisabled(True)
        self.page_count = 0
        self.client = await Client().get()
        entity_info = self.entity_input.text()
        try:
            if '@' in entity_info:
                # entity_info = int(entity_info)
                entity = await self.client.get_input_entity(entity_info)
                self.entity_id = get_input_entity_id(entity)
                # print(entity.id)
                # print(self.entity_id)
                # exit()
            elif entity_info == 'me':
                # pass
                entity = await self.client.get_input_entity('me')
                self.dump_self = True
                # print('entity', entity.to_dict())
                # exit()
                self.entity_id = self.SELF_ID
            else:
                try:
                    entity = await self.client.get_input_entity(int(entity_info))
                    self.entity_id = get_input_entity_id(entity)
                except Exception as e:
                    print(e)
                    try:
                        if str(entity_info).startswith('-100'):
                            entity_info = '-' + entity_info[4:]
                        entity = await self.client.get_input_entity(int(entity_info))
                        print('entity',entity)
                        exit()
                        # self.entity_id = get_input_entity_id(entity)
                    except Exception as e:
                        print(e)
                        raise RuntimeError('Can not get entity!')
            # print(self.entity_id)
            print('entity_info',entity_info)
            # for id in id_list:
            ex_id, is_exist = self.msg_view.exist(str(self.entity_id))
            if is_exist:
                self.ex_id = ex_id
                print('ex_id',self.ex_id)
                self.read_db(self.msg_view, self.signal, int(self.ex_id))
                # break
            else:
                kwargs = {}
                args = [self.client, entity, self.signal]
                if self.dump_self:
                    kwargs['is_bak_self'] = True
                if start_date and end_date:
                    kwargs['start_date'] = start_date
                    kwargs['end_date'] = end_date
                    dump = DumpMsg(*args, **kwargs)
                else:
                    dump = DumpMsg(*args, **kwargs)

                await dump.dump_msg()
                ex_id, is_exist = self.msg_view.exist(str(self.entity_id))
                self.ex_id = ex_id
                print('ex_id',self.ex_id)
                self.read_db(self.msg_view, self.signal, int(self.ex_id))
        except RuntimeError as e:
            print(e)
        finally:
            self.update_profile_list()
            self.dump_btn.setDisabled(False)
            print('Spinner end')
            self.spinner.delete()

    def resizeEvent(self, event):
        self.spinner.center()

class ReadDbThread(threading.Thread):
    def __init__(self, msgView, signal, entity_id, split_count=1, split_interval=5000, search_mode = None,keyword = None, is_usr_name = False):
        super().__init__()
        global COMBO_ITEM
        self.msg_view = msgView
        self.keyword = keyword
        self.entity_id = entity_id
        print('start thread!')
        self.signal = signal
        self.combo_item = COMBO_ITEM
        self.search_mode = search_mode
        self.is_usr_name = is_usr_name
        self.split_count = split_count
        self.split_interval = split_interval
        # self.interval = 500

    def run(self):
        count = 0
        print(self.combo_item[0])
        if self.search_mode == self.combo_item[0] or not self.search_mode:
            total, msg_list = self.msg_view.get(self.entity_id, keyword=self.keyword, split_count=self.split_count, split_interval=self.split_interval)
        elif self.search_mode == self.combo_item[1]:
            total, msg_list = self.msg_view.get_by_name(self.entity_id, keyword=self.keyword, is_usr_name=self.is_usr_name, split_count=self.split_count, split_interval=self.split_interval)
        elif self.search_mode == self.combo_item[2]:
            total, msg_list = self.msg_view.get_by_name(self.entity_id, keyword=self.keyword, is_usr_name=self.is_usr_name, split_count=self.split_count, split_interval=self.split_interval)
        elif self.search_mode == self.combo_item[3]:
            total, msg_list = self.msg_view.get_by_id(self.entity_id, keyword=self.keyword, split_count=self.split_count, split_interval=self.split_interval)

        print('len(msg_list)',len(msg_list))
        # print('sizeof(msg_list)',(self.get_total_size(msg_list)))
        self.signal.emit_msg_list_signal(msg_list, total, True, self.keyword)
        # listLength = len(msg_list)
        # if listLength > self.interval:
        #     while True:
        #         partList = msg_list[count:self.interval + count]
        #         if partList:
        #             self.signal.emitMsgList(partList, True if not count else False)
        #             count += self.interval
        #             print(count)
        #         else:
        #             print('Finish emit!')
        #             break
        #         time.sleep(0.1)
