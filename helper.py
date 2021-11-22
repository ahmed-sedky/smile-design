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
    try:
        Face.mouthDetection(filePath)
    except:
        Message.error(self,"Couldn't detect mouth")
        return
    fileName = Path(filePath).stem
    plotImage(self, filePath)
    setLabel(self, fileName)
    enableActions(self)

def createScene(imagePath):
    pixelMap = QPixmap(imagePath).scaled(
        560, 560, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation
    )
    item = QtWidgets.QGraphicsPixmapItem(pixelMap)
    scene = QtWidgets.QGraphicsScene()
    scene.addItem(item)
    return scene

def plotImage(self, imagePath):
    scene = createScene(imagePath)
    self.image.setScene(scene)

def plotPalette(self):
    scene = createScene("cached/color_palette")
    self.palette.setScene(scene)


def setLabel(self, label):
    self.imageName.setText(label)


def enableActions(self):
    self.discoloration.setEnabled(True)
    self.midline.setEnabled(True)

def plotTeethColor(self):
    self.teethColor.setVisible(True)
    scene = createScene("cached/teethColor")
    self.teethColor.setScene(scene)
