from PyQt5.QtWidgets import QFileDialog, QMessageBox
import image as Image
from pathlib import Path


def browsefiles(self):
    fname = QFileDialog.getOpenFileName(
        self, "Open file", "C://Users", "*.jpg;;" " *.png;;" "*.jpeg;;"
    )
    filePath = fname[0]
    fileName = Path(filePath).stem
    extensionsToCheck = (".jpg", ".png", ".jpeg")
    if fname[0].endswith(extensionsToCheck):
        Image.plotImage(self, filePath)
        setLabel(self, fileName)
    elif fname[0] != "":
        errorMssg(self, "Invalid format.")
        return
    else:
        return


def setLabel(self, label):
    self.imageName.setText(label)


def errorMssg(self, txt):
    QMessageBox.critical(self, "Error", txt)
