from PySide6.QtCore import QObject, Signal
from telethon import TelegramClient

class Signal(QObject):
    msg_signal = Signal(str,str)
    pick_entity_signal = Signal(str)
    msg_list_signal = Signal(list, int, bool, str)
    stop_signal = Signal(bool)
    signin_signal = Signal(TelegramClient)
    conf_signal = Signal()

    def emit_msg_signal(self, content: str, delay: str):
        self.msg_signal.emit(content,delay)

    def emit_pick_entity_signal(self, id: str):
        self.pick_entity_signal.emit(id)

    def emit_msg_list_signal(self,msgList: list,total: int, isStart: bool, keyword = None):
        self.msg_list_signal.emit(msgList, total, isStart, keyword)

    def emit_stop_signal(self, isStop):
        self.stop_signal.emit(isStop)

    def emit_signin_signal(self,client):
        self.signin_signal.emit(client)

    def emit_conf_signal(self):
        self.conf_signal.emit()

signal = Signal()

def get_global_signal():
    global signal
    return signal