# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'list.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QTableWidget, QTableWidgetItem, QWidget)

class Ui_ListWidget(object):
    def setupUi(self, ListWidget):
        if not ListWidget.objectName():
            ListWidget.setObjectName(u"ListWidget")
        ListWidget.resize(350, 350)
        self.gridLayout = QGridLayout(ListWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tableWidget_main = QTableWidget(ListWidget)
        self.tableWidget_main.setObjectName(u"tableWidget_main")
        self.tableWidget_main.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.tableWidget_main.setGridStyle(Qt.PenStyle.SolidLine)

        self.gridLayout.addWidget(self.tableWidget_main, 2, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.checkBox_scene = QCheckBox(ListWidget)
        self.checkBox_scene.setObjectName(u"checkBox_scene")
        self.checkBox_scene.setMinimumSize(QSize(40, 0))
        self.checkBox_scene.setMaximumSize(QSize(50, 16777215))
        self.checkBox_scene.setChecked(True)

        self.horizontalLayout.addWidget(self.checkBox_scene)

        self.checkBox_video = QCheckBox(ListWidget)
        self.checkBox_video.setObjectName(u"checkBox_video")
        self.checkBox_video.setMinimumSize(QSize(40, 0))
        self.checkBox_video.setMaximumSize(QSize(50, 16777215))
        self.checkBox_video.setChecked(True)

        self.horizontalLayout.addWidget(self.checkBox_video)

        self.checkBox_web = QCheckBox(ListWidget)
        self.checkBox_web.setObjectName(u"checkBox_web")
        self.checkBox_web.setMinimumSize(QSize(40, 0))
        self.checkBox_web.setMaximumSize(QSize(50, 16777215))
        self.checkBox_web.setChecked(True)

        self.horizontalLayout.addWidget(self.checkBox_web)

        self.checkBox_application = QCheckBox(ListWidget)
        self.checkBox_application.setObjectName(u"checkBox_application")
        self.checkBox_application.setMinimumSize(QSize(40, 0))
        self.checkBox_application.setMaximumSize(QSize(50, 16777215))
        self.checkBox_application.setChecked(True)

        self.horizontalLayout.addWidget(self.checkBox_application)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_4)

        self.checkBox_invalid = QCheckBox(ListWidget)
        self.checkBox_invalid.setObjectName(u"checkBox_invalid")
        self.checkBox_invalid.setMinimumSize(QSize(40, 0))
        self.checkBox_invalid.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.checkBox_invalid)


        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_capacity = QLabel(ListWidget)
        self.label_capacity.setObjectName(u"label_capacity")

        self.horizontalLayout_7.addWidget(self.label_capacity)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_3)

        self.btn_invalid = QPushButton(ListWidget)
        self.btn_invalid.setObjectName(u"btn_invalid")
        self.btn_invalid.setCheckable(False)
        self.btn_invalid.setAutoDefault(False)
        self.btn_invalid.setFlat(False)

        self.horizontalLayout_7.addWidget(self.btn_invalid)


        self.gridLayout.addLayout(self.horizontalLayout_7, 3, 0, 1, 1)


        self.retranslateUi(ListWidget)

        self.btn_invalid.setDefault(False)


        QMetaObject.connectSlotsByName(ListWidget)
    # setupUi

    def retranslateUi(self, ListWidget):
        ListWidget.setWindowTitle(QCoreApplication.translate("ListWidget", u"Form", None))
        self.checkBox_scene.setText(QCoreApplication.translate("ListWidget", u"\u573a\u666f", None))
        self.checkBox_video.setText(QCoreApplication.translate("ListWidget", u"\u89c6\u9891", None))
        self.checkBox_web.setText(QCoreApplication.translate("ListWidget", u"\u7f51\u9875", None))
        self.checkBox_application.setText(QCoreApplication.translate("ListWidget", u"\u5e94\u7528", None))
        self.checkBox_invalid.setText(QCoreApplication.translate("ListWidget", u"\u5931\u6548", None))
        self.label_capacity.setText(QCoreApplication.translate("ListWidget", u"\u5bb9\u91cf\uff1a0G", None))
        self.btn_invalid.setText(QCoreApplication.translate("ListWidget", u"\u5220\u9664\u5931\u6548\u8ba2\u9605", None))
    # retranslateUi

