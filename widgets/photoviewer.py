from PyQt5 import QtCore, QtWidgets


class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        self._empty = False
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        pixmap = pixmap.scaled(
            560, 560, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation
        )
        self._photo.setPixmap(pixmap)

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                if self._zoom < 10:
                    factor = 1.25
                    self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                if self._zoom != 10:
                    self.scale(factor, factor)
            else:
                self._zoom = 0
