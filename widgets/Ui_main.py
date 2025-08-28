# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QCommandLinkButton, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.setEnabled(True)
        Form.resize(640, 480)
        Form.setMinimumSize(QSize(640, 480))
        icon = QIcon()
        icon.addFile(u"../img/Management.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        Form.setWindowIcon(icon)
        self.verticalLayout_9 = QVBoxLayout(Form)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.tabWidget = QTabWidget(Form)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout = QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_error = QLabel(self.tab)
        self.label_error.setObjectName(u"label_error")
        self.label_error.setEnabled(True)
        font = QFont()
        font.setPointSize(20)
        self.label_error.setFont(font)
        self.label_error.setLineWidth(1)
        self.label_error.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label_error)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_6 = QLabel(self.tab)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(40, 0))
        self.label_6.setMaximumSize(QSize(50, 16777215))
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout.addWidget(self.label_6)

        self.checkBox_4 = QCheckBox(self.tab)
        self.checkBox_4.setObjectName(u"checkBox_4")
        self.checkBox_4.setMinimumSize(QSize(40, 0))
        self.checkBox_4.setMaximumSize(QSize(50, 16777215))
        self.checkBox_4.setChecked(True)

        self.horizontalLayout.addWidget(self.checkBox_4)

        self.checkBox_3 = QCheckBox(self.tab)
        self.checkBox_3.setObjectName(u"checkBox_3")
        self.checkBox_3.setMinimumSize(QSize(40, 0))
        self.checkBox_3.setMaximumSize(QSize(50, 16777215))
        self.checkBox_3.setChecked(True)

        self.horizontalLayout.addWidget(self.checkBox_3)

        self.checkBox_2 = QCheckBox(self.tab)
        self.checkBox_2.setObjectName(u"checkBox_2")
        self.checkBox_2.setMinimumSize(QSize(40, 0))
        self.checkBox_2.setMaximumSize(QSize(50, 16777215))
        self.checkBox_2.setChecked(True)

        self.horizontalLayout.addWidget(self.checkBox_2)

        self.checkBox = QCheckBox(self.tab)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setMinimumSize(QSize(40, 0))
        self.checkBox.setMaximumSize(QSize(50, 16777215))
        self.checkBox.setChecked(True)

        self.horizontalLayout.addWidget(self.checkBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.checkBox_5 = QCheckBox(self.tab)
        self.checkBox_5.setObjectName(u"checkBox_5")
        self.checkBox_5.setMinimumSize(QSize(40, 0))
        self.checkBox_5.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.checkBox_5)


        self.verticalLayout_6.addLayout(self.horizontalLayout)

        self.scrollArea = QScrollArea(self.tab)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setEnabled(True)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 594, 313))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_6.addWidget(self.scrollArea)


        self.verticalLayout.addLayout(self.verticalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_3 = QLabel(self.tab)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_7.addWidget(self.label_3)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_2)

        self.pushButton = QPushButton(self.tab)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setCheckable(False)
        self.pushButton.setAutoDefault(False)
        self.pushButton.setFlat(False)

        self.horizontalLayout_7.addWidget(self.pushButton)


        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.tabWidget.addTab(self.tab, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_2 = QVBoxLayout(self.tab_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(self.tab_2)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMinimumSize(QSize(0, 100))
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(160, 0))
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.label)

        self.lineEdit_steamPath = QLineEdit(self.groupBox)
        self.lineEdit_steamPath.setObjectName(u"lineEdit_steamPath")

        self.horizontalLayout_2.addWidget(self.lineEdit_steamPath)

        self.btn_steamPath = QCommandLinkButton(self.groupBox)
        self.btn_steamPath.setObjectName(u"btn_steamPath")
        self.btn_steamPath.setMaximumSize(QSize(36, 16777215))

        self.horizontalLayout_2.addWidget(self.btn_steamPath, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(160, 0))
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.label_2)

        self.lineEdit_wallpaperPath = QLineEdit(self.groupBox)
        self.lineEdit_wallpaperPath.setObjectName(u"lineEdit_wallpaperPath")

        self.horizontalLayout_3.addWidget(self.lineEdit_wallpaperPath)

        self.btn_wallpaperPath = QCommandLinkButton(self.groupBox)
        self.btn_wallpaperPath.setObjectName(u"btn_wallpaperPath")
        self.btn_wallpaperPath.setMaximumSize(QSize(36, 16777215))

        self.horizontalLayout_3.addWidget(self.btn_wallpaperPath, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(160, 0))
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_4.addWidget(self.label_4)

        self.lineEdit_wallpaperBackupPath = QLineEdit(self.groupBox)
        self.lineEdit_wallpaperBackupPath.setObjectName(u"lineEdit_wallpaperBackupPath")

        self.horizontalLayout_4.addWidget(self.lineEdit_wallpaperBackupPath)

        self.btn_wallpaperBackupPath = QCommandLinkButton(self.groupBox)
        self.btn_wallpaperBackupPath.setObjectName(u"btn_wallpaperBackupPath")
        self.btn_wallpaperBackupPath.setMaximumSize(QSize(36, 16777215))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setUnderline(False)
        self.btn_wallpaperBackupPath.setFont(font1)

        self.horizontalLayout_4.addWidget(self.btn_wallpaperBackupPath, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.groupBox_4 = QGroupBox(self.tab_2)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setMinimumSize(QSize(0, 133))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_7 = QLabel(self.groupBox_4)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setLineWidth(2)

        self.verticalLayout_4.addWidget(self.label_7)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.lineEdit_wallpaperBackupPath_2 = QLineEdit(self.groupBox_4)
        self.lineEdit_wallpaperBackupPath_2.setObjectName(u"lineEdit_wallpaperBackupPath_2")

        self.horizontalLayout_6.addWidget(self.lineEdit_wallpaperBackupPath_2)

        self.btn_backup_3 = QPushButton(self.groupBox_4)
        self.btn_backup_3.setObjectName(u"btn_backup_3")
        self.btn_backup_3.setMinimumSize(QSize(0, 23))

        self.horizontalLayout_6.addWidget(self.btn_backup_3)

        self.btn_backup_4 = QPushButton(self.groupBox_4)
        self.btn_backup_4.setObjectName(u"btn_backup_4")

        self.horizontalLayout_6.addWidget(self.btn_backup_4)


        self.verticalLayout_4.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.lineEdit_wallpaperBackupPath_3 = QLineEdit(self.groupBox_4)
        self.lineEdit_wallpaperBackupPath_3.setObjectName(u"lineEdit_wallpaperBackupPath_3")

        self.horizontalLayout_5.addWidget(self.lineEdit_wallpaperBackupPath_3)

        self.btn_backup_2 = QPushButton(self.groupBox_4)
        self.btn_backup_2.setObjectName(u"btn_backup_2")
        self.btn_backup_2.setMinimumSize(QSize(0, 23))

        self.horizontalLayout_5.addWidget(self.btn_backup_2)

        self.btn_backup = QPushButton(self.groupBox_4)
        self.btn_backup.setObjectName(u"btn_backup")

        self.horizontalLayout_5.addWidget(self.btn_backup)


        self.verticalLayout_4.addLayout(self.horizontalLayout_5)


        self.verticalLayout_2.addWidget(self.groupBox_4)

        self.groupBox_3 = QGroupBox(self.tab_2)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setMinimumSize(QSize(0, 60))
        self.label_version = QLabel(self.groupBox_3)
        self.label_version.setObjectName(u"label_version")
        self.label_version.setGeometry(QRect(10, 25, 221, 16))

        self.verticalLayout_2.addWidget(self.groupBox_3, 0, Qt.AlignmentFlag.AlignTop)

        self.verticalSpacer = QSpacerItem(20, 59, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.tab_2, "")

        self.verticalLayout_9.addWidget(self.tabWidget)

        QWidget.setTabOrder(self.tabWidget, self.scrollArea)
        QWidget.setTabOrder(self.scrollArea, self.lineEdit_steamPath)
        QWidget.setTabOrder(self.lineEdit_steamPath, self.btn_steamPath)
        QWidget.setTabOrder(self.btn_steamPath, self.lineEdit_wallpaperPath)
        QWidget.setTabOrder(self.lineEdit_wallpaperPath, self.btn_wallpaperPath)
        QWidget.setTabOrder(self.btn_wallpaperPath, self.lineEdit_wallpaperBackupPath)
        QWidget.setTabOrder(self.lineEdit_wallpaperBackupPath, self.btn_wallpaperBackupPath)
        QWidget.setTabOrder(self.btn_wallpaperBackupPath, self.btn_backup)
        QWidget.setTabOrder(self.btn_backup, self.btn_backup_2)
        QWidget.setTabOrder(self.btn_backup_2, self.btn_backup_3)
        QWidget.setTabOrder(self.btn_backup_3, self.btn_backup_4)
        QWidget.setTabOrder(self.btn_backup_4, self.lineEdit_wallpaperBackupPath_2)
        QWidget.setTabOrder(self.lineEdit_wallpaperBackupPath_2, self.lineEdit_wallpaperBackupPath_3)

        self.retranslateUi(Form)

        self.tabWidget.setCurrentIndex(0)
        self.pushButton.setDefault(False)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Wallpaper Engine Tools", None))
        self.label_error.setText(QCoreApplication.translate("Form", u"\u60a8\u672a\u5b89\u88c5Wallpaper Engine", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"\u7b5b\u9009", None))
        self.checkBox_4.setText(QCoreApplication.translate("Form", u"\u58c1\u7eb8", None))
        self.checkBox_3.setText(QCoreApplication.translate("Form", u"\u89c6\u9891", None))
        self.checkBox_2.setText(QCoreApplication.translate("Form", u"\u7f51\u9875", None))
        self.checkBox.setText(QCoreApplication.translate("Form", u"\u5e94\u7528", None))
        self.checkBox_5.setText(QCoreApplication.translate("Form", u"\u5931\u6548", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u5bb9\u91cf\uff1a0G", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"\u5220\u9664\u5931\u6548\u8ba2\u9605", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Form", u"\u5df2\u8ba2\u9605", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("Form", u"\u5907\u4efd", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"\u8f6f\u4ef6\u76ee\u5f55", None))
        self.label.setText(QCoreApplication.translate("Form", u"Steam\u5b89\u88c5\u4f4d\u7f6e", None))
        self.lineEdit_steamPath.setPlaceholderText(QCoreApplication.translate("Form", u"\u4f8b\uff1aC:\\Program Files (x86)\\Steam", None))
        self.btn_steamPath.setText("")
        self.label_2.setText(QCoreApplication.translate("Form", u"wallpaper engine\u5b89\u88c5\u4f4d\u7f6e", None))
        self.lineEdit_wallpaperPath.setPlaceholderText(QCoreApplication.translate("Form", u"\u4f8b\uff1aC:\\Program Files (x86)\\Steam\\steamapps\\common\\wallpaper_engine", None))
        self.btn_wallpaperPath.setText("")
        self.label_4.setText(QCoreApplication.translate("Form", u"\u5907\u4efd\u4f4d\u7f6e", None))
        self.lineEdit_wallpaperBackupPath.setPlaceholderText(QCoreApplication.translate("Form", u"\u4f8b\uff1aC:\\Program Files (x86)\\Steam\\steamapps\\common\\wallpaper_engine\\projects\\backup", None))
        self.btn_wallpaperBackupPath.setText("")
        self.groupBox_4.setTitle(QCoreApplication.translate("Form", u"C\u76d8\u7626\u8eab\uff08mklink\u547d\u4ee4\u751f\u6210\u8f6f\u94fe\u63a5\u76ee\u5f55\u8fc1\u79fb\u9879\u76ee\uff09", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"\u6ce8\u610f\uff1a\u751f\u6210\u8f6f\u94fe\u63a5\u5c06\u91cd\u547d\u540d\u6e90\u6587\u4ef6\u5939\uff08\u540d\u79f0+\u540e\u7f00\uff09\u9632\u6b62\u4e22\u5931\uff0c\u5982\u679c\u5931\u8d25\u8bf7\u624b\u52a8\u6539\u56de\u3002\n"
"\u8f6c\u79fb\u9879\u76ee\u4e0d\u5efa\u8bae\u4f7f\u7528\uff0c\u8bf7\u624b\u52a8\u526a\u5207\u8ba2\u9605\u76ee\u5f55", None))
        self.lineEdit_wallpaperBackupPath_2.setPlaceholderText(QCoreApplication.translate("Form", u"\u76ee\u5f55\u5730\u5740\uff1aSteam\\\\steamapps\\\\workshop\\\\content\\\\431960", None))
        self.btn_backup_3.setText(QCoreApplication.translate("Form", u"\u8ba2\u9605\u58c1\u7eb8\u751f\u6210\u8f6f\u94fe\u63a5", None))
        self.btn_backup_4.setText(QCoreApplication.translate("Form", u"\u8f6c\u79fb\u9879\u76ee", None))
        self.lineEdit_wallpaperBackupPath_3.setPlaceholderText(QCoreApplication.translate("Form", u"\u76ee\u5f55\u5730\u5740\uff1awallpaper_engine\\\\projects\\\\backup", None))
        self.btn_backup_2.setText(QCoreApplication.translate("Form", u"\u5907\u4efd\u58c1\u7eb8\u751f\u6210\u8f6f\u94fe\u63a5", None))
        self.btn_backup.setText(QCoreApplication.translate("Form", u"\u8f6c\u79fb\u9879\u76ee", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Form", u"\u5173\u4e8e", None))
        self.label_version.setText(QCoreApplication.translate("Form", u"\u7248\u672c\uff1a0", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Form", u"\u8bbe\u7f6e", None))
    # retranslateUi

