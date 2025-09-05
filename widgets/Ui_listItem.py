# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'listItem.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_ItemFrame(object):
    def setupUi(self, ItemFrame):
        if not ItemFrame.objectName():
            ItemFrame.setObjectName(u"ItemFrame")
        ItemFrame.resize(350, 140)
        ItemFrame.setMinimumSize(QSize(0, 140))
        ItemFrame.setMaximumSize(QSize(16777215, 140))
        self.horizontalLayout = QHBoxLayout(ItemFrame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_img = QLabel(ItemFrame)
        self.label_img.setObjectName(u"label_img")
        self.label_img.setMinimumSize(QSize(120, 120))
        self.label_img.setMaximumSize(QSize(120, 120))
        self.label_img.setPixmap(QPixmap(u"../img/Management.ico"))
        self.label_img.setScaledContents(True)
        self.label_img.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.label_img)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_name = QLabel(ItemFrame)
        self.label_name.setObjectName(u"label_name")

        self.horizontalLayout_2.addWidget(self.label_name)

        self.btn_name_edit = QPushButton(ItemFrame)
        self.btn_name_edit.setObjectName(u"btn_name_edit")
        self.btn_name_edit.setMinimumSize(QSize(40, 0))
        self.btn_name_edit.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayout_2.addWidget(self.btn_name_edit)

        self.btn_open = QPushButton(ItemFrame)
        self.btn_open.setObjectName(u"btn_open")
        self.btn_open.setMinimumSize(QSize(60, 0))
        self.btn_open.setMaximumSize(QSize(60, 16777215))

        self.horizontalLayout_2.addWidget(self.btn_open)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_title = QLabel(ItemFrame)
        self.label_title.setObjectName(u"label_title")

        self.horizontalLayout_3.addWidget(self.label_title)

        self.btn_title_edit = QPushButton(ItemFrame)
        self.btn_title_edit.setObjectName(u"btn_title_edit")
        self.btn_title_edit.setMinimumSize(QSize(40, 0))
        self.btn_title_edit.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayout_3.addWidget(self.btn_title_edit)

        self.btn_RePKG = QPushButton(ItemFrame)
        self.btn_RePKG.setObjectName(u"btn_RePKG")
        self.btn_RePKG.setMinimumSize(QSize(60, 0))
        self.btn_RePKG.setMaximumSize(QSize(60, 16777215))

        self.horizontalLayout_3.addWidget(self.btn_RePKG)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.label_note = QLabel(ItemFrame)
        self.label_note.setObjectName(u"label_note")

        self.verticalLayout_2.addWidget(self.label_note)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.verticalLayout_2)


        self.retranslateUi(ItemFrame)

        QMetaObject.connectSlotsByName(ItemFrame)
    # setupUi

    def retranslateUi(self, ItemFrame):
        ItemFrame.setWindowTitle(QCoreApplication.translate("ItemFrame", u"Frame", None))
        self.label_img.setText("")
        self.label_name.setText(QCoreApplication.translate("ItemFrame", u"\u6587\u4ef6\u5939\uff1a\u7c7b\u578b", None))
        self.btn_name_edit.setText(QCoreApplication.translate("ItemFrame", u"\u4fee\u6539", None))
        self.btn_open.setText(QCoreApplication.translate("ItemFrame", u"\u6253\u5f00", None))
        self.label_title.setText(QCoreApplication.translate("ItemFrame", u"\u6807\u9898", None))
        self.btn_title_edit.setText(QCoreApplication.translate("ItemFrame", u"\u4fee\u6539", None))
        self.btn_RePKG.setText(QCoreApplication.translate("ItemFrame", u"\u63d0\u53d6", None))
        self.label_note.setText(QCoreApplication.translate("ItemFrame", u"\u5185\u5bb9", None))
    # retranslateUi

