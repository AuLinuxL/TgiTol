# if __name__ == '__main__':
#     import sys
#     import os
#
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     project_root = os.path.abspath(os.path.join(current_dir, '../../'))
#     sys.path.append(project_root)

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt, Signal)
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

from qasync import asyncSlot

from backend.db import get_session
from backend.models import Config

from ui.component.MsgBox import warning
import asyncio, threading, time
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from util import get_ui_path, center, trigger_show_layout

# class SignalEmitter(QObject):
#     finished = Signal(bool, int, str)
#     error = Signal(str)
#     warning = Signal(str)

# class SignInWorker(threading.Thread):
#     def __init__(self):
#         super().__init__()
#         # self.client = TelegramClient("/var/home/kblur/PycharmProjects/TgiTol/.venv/src/conf/anon.session", '27421121', 'e56e6500b6773b6b8a1a461795289c02')
#         session = getSession()
#         api_conf = session.query(Config).first()
#         api_id = api_conf.api_id
#         session.close()
#         api_hash = api_conf.api_hash
#         prefix = get_prefix()
#         self.client = TelegramClient(f"{prefix}conf/anon.session", api_id, api_hash)
#         self.phone = None
#         self.code = None
#         self.password = None
#         self.step = 1
#         self.signals = SignalEmitter()
#         self.signals.warning.emit('test')

#     def run(self):
#         self.loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(self.loop)
#         while True:
#             try:
#                 if not self.client.is_connected():
#                     self.loop.run_until_complete(self.client.connect())
#                 if self.step == 1:
#                     try:
#                         self.step = 0
#                         self.loop.run_until_complete(self.client.send_code_request(self.phone))
#                         result = True
#                         self.signals.finished.emit(result, 1, "")
#                     except Exception as e:
#                         self.signals.error.emit(str(e))
#                         result = False
#                     # self.signals.error.emit(result, 1, "")
#                 elif self.step == 2:
#                     try:
#                         self.step = 0
#                         self.loop.run_until_complete(self.client.sign_in(phone=self.phone, code=self.code))
#                         result = True
#                         self.signals.finished.emit(result, 2, "")
#                         break
#                     except SessionPasswordNeededError:
#                         print('need psw')
#                         self.signals.finished.emit(False, 2, "Password needed")
#                     except Exception as e:
#                         self.signals.error.emit(str(e))
#                         result = False
#                 elif self.step == 3:
#                     try:
#                         self.step = 0
#                         self.loop.run_until_complete(self.client.sign_in(password=self.password))
#                         result = True
#                         # self.loop.close()
#                         # self.client.disconnect()
#                         self.signals.warning.emit('Log in success!')
#                         time.sleep(2)
#                         self.signals.finished.emit(result, 3, "")
#                         break
#                     except Exception as e:
#                         self.signals.error.emit(str(e))
#                         result = False
#             except Exception as e:
#                 self.signals.error.emit(str(e))


# class SignInDialog(QDialog):
#     def __init__(self):
#         super().__init__()
#         prefix = get_prefix()
#         ui_file = QFile(get_ui_path("SignInDialog.ui"))
#         ui_file.open(QFile.ReadOnly)

#         loader = QUiLoader()
#         self.page = loader.load(ui_file)
#         ui_file.close()

#         layout = QVBoxLayout()
#         layout.addWidget(self.page)
#         self.setLayout(layout)

#         self.setWindowTitle('SignIn')
#         self.setup_ui()
#         center(self.page)

#         self.step_count = 1
#         self.worker = None
#         self.worker_start = False

#     def __del__(self):
#         try:
#             self.close()
#             self.worker.loop.close()
#             self.worker.client.disconnect()
#             self.worker.join()
#         except Exception as e:
#             warning(self,str(e))

#     def setup_ui(self):
#         self.signin_btn: QPushButton = self.page.signInBtn
#         self.phone_input: QLineEdit = self.page.phoneInput
#         self.code_input: QLineEdit = self.page.codeInput
#         self.pwd_input: QLineEdit = self.page.pwdInput

#         self.code_layout = self.page.codeLayout
#         self.pwd_layout = self.page.pwdLayout

#         trigger_show_layout(self.code_layout, True)
#         trigger_show_layout(self.pwd_layout, True)

#         self.signin_btn.setText('Next')
#         self.signin_btn.clicked.connect(self.on_sign_in)

#     # def on_sign_in(self):
#     #     self.signin_btn.setEnabled(False)
#     #     if not self.worker:
#     #         self.worker = SignInWorker()
#     #         self.worker.signals.finished.connect(self.on_worker_finished)
#     #         self.worker.signals.error.connect(self.on_worker_error)
#     #         self.worker.signals.warning.connect(self.on_worker_warning)

#     #     if self.step_count == 1:
#     #         self.worker.phone = self.phone_input.text()
#     #     elif self.step_count == 2:
#     #         self.worker.code = self.code_input.text()
#     #     elif self.step_count == 3:
#     #         self.worker.password = self.pwd_input.text()

#     #     self.worker.step = self.step_count
#     #     if not self.worker_start:
#     #         self.worker.start()
#     #         self.worker_start = True

#     # def on_worker_finished(self, result, step, message):
#     #     self.signin_btn.setEnabled(True)
#     #     if step == 1:
#     #         if result:
#     #             self.step_count = 2
#     #             trigger_show_layout(self.code_layout, False)
#     #             self.signin_btn.setText('Sign in')
#     #         else:
#     #             self.warning(self,'Phone Verify Error!')
#     #     elif step == 2:
#     #         if result:
#     #             self.close()
#     #         else:
#     #             if message == "Password needed":
#     #                 self.step_count = 3
#     #                 trigger_show_layout(self.pwd_layout, False)
#     #             else:
#     #                 self.warning(self,'Code Verify Error!')
#     #     elif step == 3:
#     #         if result:
#     #             self.worker.join()
#     #             self.close()
#     #         else:
#     #             self.warning(self,'Password Verify Error!')

#     # def on_worker_error(self, error_message):
#     #     self.signin_btn.setEnabled(True)
#     #     warning(self,f'Error: {error_message}')

#     # def on_worker_warning(self, warning_message):
#     #     warning(self,warning_message)

# if __name__ == '__main__':
#     QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
#     app = QApplication([])
#     dialog = SignInDialog()
#     dialog.page.show()
#     app.exec()


class SignInDialog(QDialog):
    def __init__(self, client):
        super().__init__()
        ui_file = QFile(get_ui_path("SignInDialog.ui"))
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.page = loader.load(ui_file)
        ui_file.close()

        layout = QVBoxLayout()
        layout.addWidget(self.page)
        self.setLayout(layout)

        self.setWindowTitle('SignIn')
        self.setup_ui()

        self.client = client

        self.step_count = 1

    def setup_ui(self):
        self.signin_btn:QPushButton = self.page.signInBtn
        self.phone_input: QLineEdit = self.page.phoneInput
        self.code_input: QLineEdit = self.page.codeInput
        self.pwd_input: QLineEdit = self.page.pwdInput

        self.code_layout = self.page.codeLayout
        self.pwd_layout = self.page.pwdLayout

        trigger_show_layout(self.code_layout,False)
        trigger_show_layout(self.pwd_layout,False)

        self.signin_btn.setText('Next')
        self.signin_btn.clicked.connect(self.on_sign_in)

    @asyncSlot()
    async def on_sign_in(self):
        match self.step_count:
            case 1:
                self.phone = self.phone_input.text()
                if not len(self.phone):
                    warning(self,'Phone Error!')
                    return
                result = await self.client.send_code_request(self.phone)
                # loop = asyncio.get_event_loop()
                # result = await loop.run_in_executor(None, self.client.send_code_request, self.phone)
                if result:
                    self.step_count += 1
                    trigger_show_layout(self.code_layout,True)
                    return
                else:
                    warning(self,'Phone Verify Error!')
                    return
            case 2:
                self.code = self.code_input.text()
                if not len(self.code):
                    warning(self,'Code Error!')
                    return
                try:
                    if await self.client.sign_in(self.phone, self.code):
                        self.close()
                    else:
                        warning(self, 'Code Verify Error!')
                        return
                except SessionPasswordNeededError:
                    self.step_count += 1
                    trigger_show_layout(self.pwd_layout,True)
                    return
                    # await self.client.sign_in(password=password)
            case 3:
                self.password = self.pwd_input.text()
                if not len(self.password):
                    warning(self, 'Code Error!')
                    return
                if await self.client.sign_in(password=self.password):
                    self.client.disconnect()
                    self.close()
                else:
                    warning(self, 'Password Verify Error!')
                    return