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
    global originalTemplate
    global currentTemplate

    try:
        removePixmapItem(self, originalTemplate)
        removePixmapItem(self, currentTemplate)
    except:
        pass

    try:
        Face.mouthDetection()
    except:
        Message.error(self, "Couldn't detect mouth")
        return
    plotImage(self, filePath)
    setLabel(self, "Before & After")
    disableTeethColoration(self)
    enableActions(self)
    Face.checkAll(self)


def plotImage(self, imagePath):
    self.image.setPhoto(QPixmap(imagePath))


def plotImageAfter(self, imagePath):
    self.imageAfter.setPhoto(QPixmap(imagePath))


def plotPalette(self):
    self.palette.setPhoto(QPixmap("cached/color_palette"))


def plotTeethColor(self):
    self.teethColor.setPhoto(QPixmap("cached/teethColor.png"))


def createPixmapItem(self, imagePath, size, offset=QtCore.QPointF(0, 0)):
    pixelMap = QPixmap(imagePath).scaled(
        int(size[0]),
        int(size[1]),
        QtCore.Qt.KeepAspectRatio,
        QtCore.Qt.FastTransformation,
    )
    scene = self.imageAfter.scene()

    offset.setX(offset.x() * scene.width())
    offset.setY(offset.y() * scene.height())
    item = QtWidgets.QGraphicsPixmapItem(pixelMap)
    item.setOffset(offset)

    return item


def setLabel(self, label):
    self.statusLabel.setText(label)


def enableTeethColoration(self):
    self.colorsWidget.setVisible(True)
    self.colorsComboBox.setCurrentIndex(-1)


def enableActions(self):
    self.checkAll.setEnabled(True)
    self.scaleTemplateUp.setEnabled(True)
    self.scaleTemplateDown.setEnabled(True)
    self.shapesWidget.setVisible(True)
    self.shapesComboBox.setCurrentIndex(-1)


def disableTeethColoration(self):
    self.colorsWidget.setVisible(False)


def colorsComboBoxChanged(self, text):
    Face.teethColoring(text)
    plotImageAfter(self, Face.finalImagePath)
    self.shapesComboBox.setCurrentIndex(-1)


def shapesComboBoxChanged(self, text):
    global originalTemplate
    global currentTemplate
    global currentTemplateScale

    currentTemplateScale = 1
    try:
        removePixmapItem(self, originalTemplate)
        removePixmapItem(self, currentTemplate)
    except:
        pass

    originalTemplate = Face.templateMatching(self, text)
    originalTemplate.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)

    currentTemplate = QtWidgets.QGraphicsPixmapItem(originalTemplate.pixmap())
    currentTemplate.setOffset(originalTemplate.offset())
    self.imageAfter.scene().addItem(originalTemplate)
    self.colorsComboBox.setCurrentIndex(-1)


def removePixmapItem(self, item):
    try:
        self.imageAfter.scene().removeItem(item)
    except:
        pass


def scaleTemplate(self, scale):
    global currentTemplate
    global originalTemplate
    global currentTemplateScale

    try:
        currentTemplateScale *= scale
        removePixmapItem(self, originalTemplate)
        removePixmapItem(self, currentTemplate)
        currentTemplate.setPixmap(originalTemplate.pixmap())

        templateSize = (
            originalTemplate.pixmap().width(),
            originalTemplate.pixmap().height(),
        )
        currentTemplate.setPixmap(
            currentTemplate.pixmap().scaled(
                int(templateSize[0] * currentTemplateScale),
                int(templateSize[1] * currentTemplateScale),
                QtCore.Qt.IgnoreAspectRatio,
                QtCore.Qt.FastTransformation,
            )
        )
        currentTemplate.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.imageAfter.scene().addItem(currentTemplate)
    except:
        pass
