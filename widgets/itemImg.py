from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ItemImg(QWidget):
    def setContent(self, data, imgWidth, authorblock = False):
        # verticalLayout = QVBoxLayout(self)
        # verticalLayout.setContentsMargins(0, 0, 0, 0)
        itemBox = QLabel('', self)
        itemBox.resize(imgWidth, imgWidth)
        itemBox.setMinimumSize(QSize(imgWidth, imgWidth))
        itemBox.setMaximumSize(QSize(imgWidth, imgWidth))
        # itemBox.setScaledContents(True)
        # itemBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        imgPath = data["previewsmall"] if "previewsmall" in data else u":/img/dir.png"
        itemBox.setPixmap(QPixmap(imgPath).scaled(imgWidth, imgWidth, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # verticalLayout.addWidget(itemBox)
        
        txtBox = QLabel(data["title"], self)
        styleStr = u'font-size: 12px;'
        styleStr += u'color: rgb(255, 0, 0);' if data['invalid'] else u'color: rgb(255, 255, 255);'
        styleStr += u'background-color: rgba(255, 0, 0, 0.7);' if authorblock else u'background-color: rgba(0, 0, 0, 0.7);'
        txtBox.setStyleSheet(styleStr)
        txtBox.setMargin(6)
        txtBox.resize(imgWidth, 30)
        txtBox.move(0, imgWidth - 30)
        tag = data["filesizelabel"] if "filesizelabel" in data else ""
        if tag:
            tagBox = QLabel(tag, self)
            styleStr = u'font-size: 9px;color: rgb(255, 255, 255);border-radius: 4px;padding: 4px 4px 4px 14px;'
            styleStr += u'background-color: rgba(0, 0, 0, 0.7);' 
            if data["source"] == "wallpaper":
                styleStr += u'background-color: rgba(0, 254, 255, 0.7);' 
            elif data["source"] == "tempData":
                styleStr += u'background-color: rgba(255, 128, 0, 0.7);' 
            elif "storagepath" in data and data["storagepath"] != "":
                styleStr += u'background-color: rgba(108, 148, 212, 0.7);' 
            else:
                styleStr += u'background-color: rgba(0, 0, 0, 0.7);' 
            tagBox.setStyleSheet(styleStr)
            # tagBox.setContentsMargins(16, 6, 6, 6)
            tagBox.move(-10, 5)

        # verticalLayout.addWidget(txtBox)