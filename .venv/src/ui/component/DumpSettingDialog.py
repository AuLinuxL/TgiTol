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
from backend.views import ChannelView, GroupView
from datetime import datetime

from util import center, get_ui_path
from qasync import asyncSlot

from tel.SyncEntity import get_entity_list

import asyncio

class DumpSettingDialog(QDialog):
    dump_mode = ('date', 'id', 'all')

    def __init__(self):
        super().__init__()
        ui_file = QFile(get_ui_path("DumpSettingDialog.ui"))
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.page = loader.load(ui_file)
        ui_file.close()

        layout = QVBoxLayout()
        layout.addWidget(self.page)
        self.setLayout(layout)

        self.mode = self.dump_mode[0]

        # self.center(self.page)
        self.setWindowTitle('Setting')
        self.resize(500,100)
        # self.initEntity()
        center(self.page)
        self.setup_db()
        self.setup_ui()
        self.load_conf()

    def setup_db(self):
        self.session = get_session()
        self.confView = configView(self.session)
        self.conf = self.confView.get()

    def setup_ui(self):
        self.dump_mode_combo: QComboBox = self.page.dumpModeCombo
        self.apply_btn: QPushButton = self.page.applyBtn
        self.cancel_btn: QPushButton = self.page.cancelBtn
        self.f_year_input: QLineEdit = self.page.fYearInput
        self.f_month_input: QLineEdit = self.page.fMonthInput
        self.f_day_input: QLineEdit = self.page.fDayInput
        self.t_year_input: QLineEdit = self.page.tYearInput
        self.t_month_input: QLineEdit = self.page.tMonthInput
        self.t_day_input: QLineEdit = self.page.tDayInput
        self.f_id_input: QLineEdit = self.page.fIdInput
        self.t_id_input: QLineEdit = self.page.tIdInput

        self.cancel_btn.clicked.connect(self.on_cancel)
        self.apply_btn.clicked.connect(self.on_apply)
        self.dump_mode_combo.currentIndexChanged.connect(self.on_mode_change)

    def loadConf(self):
        self.dump_mode_combo.setCurrentIndex(self.conf.dump_mode)

    def on_cancel(self):
        self.close()

    def on_mode_change(self, index):
        match index:
            case 0:
                self.mode = self.dump_mode[0]
            case 1:
                self.mode = self.dump_mode[1]
            case 2:
                self.mode = self.dump_mode[2]

        self.confView.save(dump_mode, self.mode)

    def load_conf(self):
        fdate = self.conf.dump_fdate
        tdate = self.conf.dump_tdate
        if fdate:
            self.f_year_input.setText(fdate.year)
            self.f_month_input.setText(fdate.month)
            self.f_day_input.setText(fdate.day)
        if tdate:
            self.t_year_input.setText(tdate.year)
            self.t_month_input.setText(tdate.month)
            self.t_day_input.setText(tdate.day)
        fid = str(self.conf.dump_fid) if self.conf.dump_fid else ''
        tid = str(self.conf.dump_tid) if self.conf.dump_tid else ''
        self.f_id_input.setText(fid)
        self.t_id_input.setText(tid)

    def save_conf(self):
        date_fields = {
            "fyear": self.f_year_input.text(),
            "fmonth": self.f_month_input.text(),
            "fday": self.f_day_input.text(),
            "tyear": self.t_year_input.text(),
            "tmonth": self.t_month_input.text(),
            "tday": self.t_day_input.text(),
            "fid": self.f_id_input.text(),
            "tid": self.t_id_input.text()
        }

        for key, value in date_fields.items():
            if value:
                date_fields[key] = int(value)
            else:
                print(f"Invalid input for {key}: {value}")
                return

        from_date = f"{date_fields[fyear]}-{date_fields[fmonth]}-{date_fields[fday]}"
        to_date = f"{date_fields[tyear]}-{date_fields[tmonth]}-{date_fields[tday]}"

        fdate = datetime.strptime(from_date_str, "%Y-%m-%d").date()
        tdate = datetime.strptime(to_date_str, "%Y-%m-%d").date()

        if fdate < tdate:
            print("From date is earlier than to date")
            return

        if fid > tid:
            print("From id is bigger than to id")
            return

        self.confView.save(dump_fdate,from_date)
        self.confView.save(dump_tdate,to_date)
        self.confView.save(dump_fid,date_fields["fid"])
        self.confView.save(dump_tid, date_fields["tid"])

    def on_apply(self):
        self.save_date()
        # Save data