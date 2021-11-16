from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, QtCore
from pathlib import Path
import face as Face
import message as Message


def browsefiles(self):
    fname = QFileDialog.getOpenFileName(
        self, "Open file", "../", "*.jpg;;" " *.png;;" "*.jpeg;;"
    )
    filePath = fname[0]
    extensionsToCheck = (".jpg", ".png", ".jpeg")
    if fname[0].endswith(extensionsToCheck):
        start(self, filePath)
    elif fname[0] != "":
        Message.error(self, "Invalid format.")
        return
    else:
        return


def start(self, filePath):
    fileName = Path(filePath).stem
    plotImage(self, filePath)
    setLabel(self, fileName)
    Face.mouthDetection(filePath)
    enableActions(self)


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
