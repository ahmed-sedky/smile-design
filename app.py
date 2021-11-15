from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QMainWindow, QWidget
import sys
import helper as helper


class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("app.ui", self)
        self.openImage.triggered.connect(lambda: helper.browsefiles(self))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())
