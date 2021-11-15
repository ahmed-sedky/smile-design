from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, QtCore


def plotImage(self, imagePath):
    pixelMap = QPixmap(imagePath).scaled(
        560, 560, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation
    )
    item = QtWidgets.QGraphicsPixmapItem(pixelMap)
    scene = QtWidgets.QGraphicsScene()
    scene.addItem(item)
    self.image.setScene(scene)
