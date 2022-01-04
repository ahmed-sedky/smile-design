from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, QtCore
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
    global item

    item = QtWidgets.QGraphicsPixmapItem()
    try:
        Face.mouthDetection()
    except:
        Message.error(self, "Couldn't detect mouth")
        return
    plotImage(self, filePath)
    setLabel(self, "Before & After")
    disableTeethColoration(self)
    enableFaceShapes(self)
    Face.checkAll(self)


def plotImage(self, imagePath):
    self.image.setPhoto(QPixmap(imagePath))


def plotImageAfter(self, imagePath):
    global item
    try:
        self.imageAfter.scene().removeItem(item)
    except:
        pass
    self.imageAfter.setPhoto(QPixmap(imagePath))


def plotPalette(self):
    scene = createScene("cached/color_palette",(560,560))
    self.palette.setScene(scene)


def plotTeethColor(self):
    scene = createScene("cached/teethColor.png",(560,560))
    self.teethColor.setScene(scene)


def createScene(imagePath, size):
    item = createPixmapItem(imagePath, size)
    scene = QtWidgets.QGraphicsScene()
    scene.addItem(item)
    return scene

def createPixmapItem(imagePath, size, offset=QtCore.QPointF(0,0)):
    pixelMap = QPixmap(imagePath).scaled(
        int(size[0]*0.7), int(size[1]*0.7), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation
    )
    item = QtWidgets.QGraphicsPixmapItem(pixelMap)
    item.setOffset(offset)

    return item


def setLabel(self, label):
    self.statusLabel.setText(label)


def enableTeethColoration(self):
    self.colorsWidget.setVisible(True)
    self.colorsComboBox.setCurrentIndex(-1)

def enableFaceShapes(self):
    self.shapesWidget.setVisible(True)
    self.shapesComboBox.setCurrentIndex(-1)

def disableTeethColoration(self):
    self.colorsWidget.setVisible(False)


def colorsComboBoxChanged(self, text):
    Face.teethColoring(text)
    plotImageAfter(self, Face.finalImagePath)
    self.shapesComboBox.setCurrentIndex(-1)

def shapesComboBoxChanged(self, text):
    global item
    try:
        self.imageAfter.scene().removeItem(item)
    except:
        pass
    item = Face.templateMatching(text)
    item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable,True)
    
    self.imageAfter.scene().addItem(item)
    self.colorsComboBox.setCurrentIndex(-1)