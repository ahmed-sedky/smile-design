from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow
import sys
import helper as Helper
import face as Face


class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("app.ui", self)
        self.showMaximized()
        Helper.plotPalette(self)
        self.colorsWidget.setVisible(False)
        self.shapesWidget.setVisible(False)
        self.openImage.triggered.connect(lambda: Helper.browsefiles(self))
        self.checkAll.triggered.connect(lambda: Face.showResults(self))
        self.colorsComboBox.activated[str].connect(
            lambda text: Helper.colorsComboBoxChanged(self, text)
        )
        self.shapesComboBox.activated[str].connect(
            lambda text: Helper.shapesComboBoxChanged(self, text)
        )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())
