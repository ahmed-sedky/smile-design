from PyQt5.QtWidgets import QMessageBox


def error(self, txt):
    QMessageBox.critical(self, "Error", txt)


def info(self, txt):
    QMessageBox.information(self, "Results", txt)
