from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, QtCore
from pathlib import Path
import face as Face


def browsefiles(self):
    fname = QFileDialog.getOpenFileName(
        self, "Open file", "C://Users", "*.jpg;;" " *.png;;" "*.jpeg;;"
    )
    filePath = fname[0]
    fileName = Path(filePath).stem
    extensionsToCheck = (".jpg", ".png", ".jpeg")
    if fname[0].endswith(extensionsToCheck):
        plotImage(self, filePath)
        setLabel(self, fileName)
        Face.mouthDetection(filePath)
        enableActions(self)
    elif fname[0] != "":
        errorMssg(self, "Invalid format.")
        return
    else:
        return


def plotImage(self, imagePath):
    pixelMap = QPixmap(imagePath).scaled(
        560, 560, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation
    )
    item = QtWidgets.QGraphicsPixmapItem(pixelMap)
    scene = QtWidgets.QGraphicsScene()
    scene.addItem(item)
    self.image.setScene(scene)


def setLabel(self, label):
    self.imageName.setText(label)


def enableActions(self):
    self.discoloration.setEnabled(True)
    self.midline.setEnabled(True)


def errorMssg(self, txt):
    QMessageBox.critical(self, "Error", txt)


def popMssg(self, txt):
    QMessageBox.information(self, "Result", txt)
