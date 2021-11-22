from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow
import sys
import helper as Helper
import face as Face


class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("app.ui", self)
        Helper.plotPalette(self)
        self.palette.setVisible(False)
        self.teethColor.setVisible(False)
        self.openImage.triggered.connect(lambda: Helper.browsefiles(self))
        self.discoloration.triggered.connect(lambda: Face.checkDiscoloration(self))
        self.midline.triggered.connect(lambda: Face.checkMidline(self))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())
