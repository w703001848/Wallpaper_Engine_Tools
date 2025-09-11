from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ItemImg(QWidget):
    def setContent(self, imgWidth, imgPath, name):
        verticalLayout = QVBoxLayout(self)
        verticalLayout.setContentsMargins(0, 0, 0, 0)
        
        itemBox = QLabel()
        itemBox.setMinimumSize(QSize(imgWidth, imgWidth))
        itemBox.setMaximumSize(QSize(imgWidth, imgWidth))
        # itemBox.setScaledContents(True)
        # itemBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        itemBox.setPixmap(QPixmap(imgPath).scaled(imgWidth, imgWidth, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        verticalLayout.addWidget(itemBox)
        
        txtBox = QLabel(name)
        txtBox.setStyleSheet(u"color: rgb(255, 255, 255);background-color: rgba(0, 0, 0, 0.7);")
        txtBox.setMargin(6)
        verticalLayout.addWidget(txtBox)