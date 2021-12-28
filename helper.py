from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, QtCore
from pathlib import Path
import face as Face
import message as Message


def browsefiles(self):
    global filePath

    fname = QFileDialog.getOpenFileName(
        self, "Open file", "./test", "*.jpg;;" " *.png;;" "*.jpeg;;"
    )
    filePath = fname[0]
    extensionsToCheck = (".jpg", ".png", ".jpeg", ".jfif")
    if fname[0].endswith(extensionsToCheck):
        start(self)
    elif fname[0] != "":
        Message.error(self, "Invalid format.")
        return
    else:
        return


def start(self):
    try:
        Face.mouthDetection()
    except:
        Message.error(self, "Couldn't detect mouth")
        return
    fileName = Path(filePath).stem
    plotImage(self, filePath)
    setLabel(self, fileName)
    enableActions(self)
    disableTeethColoration(self)


def plotImage(self, imagePath):
    scene = createScene(imagePath)
    self.image.setScene(scene)


def plotPalette(self):
    scene = createScene("cached/color_palette")
    self.palette.setScene(scene)


def plotTeethColor(self):
    scene = createScene("cached/teethColor.png")
    self.teethColor.setScene(scene)


def createScene(imagePath):
    pixelMap = QPixmap(imagePath).scaled(
        560, 560, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation
    )
    item = QtWidgets.QGraphicsPixmapItem(pixelMap)
    scene = QtWidgets.QGraphicsScene()
    scene.addItem(item)
    return scene


def setLabel(self, label):
    self.imageName.setText(label)


def enableActions(self):
    self.checkAll.setEnabled(True)


def enableTeethColoration(self):
    self.colorsWidget.setVisible(True)
    self.colorsComboBox.setCurrentIndex(-1)


def disableTeethColoration(self):
    self.colorsWidget.setVisible(False)


def comboBoxChanged(self, text):
    Face.teethColoring(text)
    Face.templateMatching()
    plotImage(self, Face.imagePath)
