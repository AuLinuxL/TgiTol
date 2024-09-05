from PySide6.QtWidgets import QMessageBox

def warning(context, msg):
    ret = QMessageBox.warning(context, "Error",
                                   msg, QMessageBox.StandardButton.Cancel)
    return ret