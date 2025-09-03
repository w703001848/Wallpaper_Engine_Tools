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
from PySide6.QtWidgets import (QApplication, QCommandLinkButton, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MainForm(object):
    def setupUi(self, MainForm):
        if not MainForm.objectName():
            MainForm.setObjectName(u"MainForm")
        MainForm.setEnabled(True)
        MainForm.resize(640, 480)
        MainForm.setMinimumSize(QSize(640, 480))
        icon = QIcon()
        icon.addFile(u"../img/Management.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainForm.setWindowIcon(icon)
        self.gridLayout = QGridLayout(MainForm)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(MainForm)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_main = QWidget()
        self.tab_main.setObjectName(u"tab_main")
        self.gridLayout_4 = QGridLayout(self.tab_main)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.tabWidget.addTab(self.tab_main, "")
        self.tab_backup = QWidget()
        self.tab_backup.setObjectName(u"tab_backup")
        self.gridLayout_2 = QGridLayout(self.tab_backup)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabWidget.addTab(self.tab_backup, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_5 = QVBoxLayout(self.tab)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.lineEdit_repkg = QLineEdit(self.tab)
        self.lineEdit_repkg.setObjectName(u"lineEdit_repkg")

        self.horizontalLayout_8.addWidget(self.lineEdit_repkg)

        self.btn_repkgPath = QPushButton(self.tab)
        self.btn_repkgPath.setObjectName(u"btn_repkgPath")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditFind))
        self.btn_repkgPath.setIcon(icon1)

        self.horizontalLayout_8.addWidget(self.btn_repkgPath)

        self.btn_repkg = QPushButton(self.tab)
        self.btn_repkg.setObjectName(u"btn_repkg")

        self.horizontalLayout_8.addWidget(self.btn_repkg)


        self.verticalLayout_5.addLayout(self.horizontalLayout_8)

        self.tableWidget_repkg = QTableWidget(self.tab)
        if (self.tableWidget_repkg.columnCount() < 4):
            self.tableWidget_repkg.setColumnCount(4)
        self.tableWidget_repkg.setObjectName(u"tableWidget_repkg")
        self.tableWidget_repkg.setFrameShape(QFrame.Shape.NoFrame)
        self.tableWidget_repkg.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.tableWidget_repkg.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableWidget_repkg.setColumnCount(4)
        self.tableWidget_repkg.horizontalHeader().setVisible(False)
        self.tableWidget_repkg.verticalHeader().setVisible(False)

        self.verticalLayout_5.addWidget(self.tableWidget_repkg)

        self.tabWidget.addTab(self.tab, "")
        self.tab_mklink = QWidget()
        self.tab_mklink.setObjectName(u"tab_mklink")
        self.verticalLayout_7 = QVBoxLayout(self.tab_mklink)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_7 = QLabel(self.tab_mklink)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setLineWidth(2)

        self.horizontalLayout_4.addWidget(self.label_7)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.btn_mklink_new = QPushButton(self.tab_mklink)
        self.btn_mklink_new.setObjectName(u"btn_mklink_new")
        self.btn_mklink_new.setMinimumSize(QSize(0, 45))
        self.btn_mklink_new.setMaximumSize(QSize(80, 16777215))
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.FolderNew))
        self.btn_mklink_new.setIcon(icon2)

        self.horizontalLayout_4.addWidget(self.btn_mklink_new)


        self.verticalLayout_7.addLayout(self.horizontalLayout_4)

        self.listWidget_mklink = QListWidget(self.tab_mklink)
        self.listWidget_mklink.setObjectName(u"listWidget_mklink")

        self.verticalLayout_7.addWidget(self.listWidget_mklink)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_3 = QLabel(self.tab_mklink)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(160, 0))
        self.label_3.setMaximumSize(QSize(160, 16777215))
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.label_3)

        self.lineEdit_mklink_path = QLineEdit(self.tab_mklink)
        self.lineEdit_mklink_path.setObjectName(u"lineEdit_mklink_path")
        self.lineEdit_mklink_path.setEnabled(False)

        self.horizontalLayout_5.addWidget(self.lineEdit_mklink_path)

        self.btn_mklink_open_old = QPushButton(self.tab_mklink)
        self.btn_mklink_open_old.setObjectName(u"btn_mklink_open_old")
        self.btn_mklink_open_old.setMaximumSize(QSize(48, 16777215))

        self.horizontalLayout_5.addWidget(self.btn_mklink_open_old)


        self.verticalLayout_7.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_5 = QLabel(self.tab_mklink)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(160, 0))
        self.label_5.setMaximumSize(QSize(160, 16777215))
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_7.addWidget(self.label_5)

        self.lineEdit_mklink_path_new = QLineEdit(self.tab_mklink)
        self.lineEdit_mklink_path_new.setObjectName(u"lineEdit_mklink_path_new")

        self.horizontalLayout_7.addWidget(self.lineEdit_mklink_path_new)

        self.btn_mklink_open = QPushButton(self.tab_mklink)
        self.btn_mklink_open.setObjectName(u"btn_mklink_open")
        self.btn_mklink_open.setMaximumSize(QSize(48, 16777215))

        self.horizontalLayout_7.addWidget(self.btn_mklink_open)


        self.verticalLayout_7.addLayout(self.horizontalLayout_7)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btn_mklink_create = QPushButton(self.tab_mklink)
        self.btn_mklink_create.setObjectName(u"btn_mklink_create")
        self.btn_mklink_create.setMinimumSize(QSize(240, 23))

        self.horizontalLayout.addWidget(self.btn_mklink_create)

        self.btn_mklink_restore = QPushButton(self.tab_mklink)
        self.btn_mklink_restore.setObjectName(u"btn_mklink_restore")
        self.btn_mklink_restore.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout.addWidget(self.btn_mklink_restore)

        self.btn_dir_move = QPushButton(self.tab_mklink)
        self.btn_dir_move.setObjectName(u"btn_dir_move")
        self.btn_dir_move.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout.addWidget(self.btn_dir_move)

        self.btn_mklink_remove = QPushButton(self.tab_mklink)
        self.btn_mklink_remove.setObjectName(u"btn_mklink_remove")
        self.btn_mklink_remove.setMaximumSize(QSize(80, 16777215))
        self.btn_mklink_remove.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 85, 0);")

        self.horizontalLayout.addWidget(self.btn_mklink_remove)


        self.verticalLayout_7.addLayout(self.horizontalLayout)

        self.tabWidget.addTab(self.tab_mklink, "")
        self.tab_set = QWidget()
        self.tab_set.setObjectName(u"tab_set")
        self.gridLayout_3 = QGridLayout(self.tab_set)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_1 = QScrollArea(self.tab_set)
        self.scrollArea_1.setObjectName(u"scrollArea_1")
        self.scrollArea_1.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea_1.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea_1.setWidgetResizable(True)
        self.scrollAreaWidgetContents_1 = QWidget()
        self.scrollAreaWidgetContents_1.setObjectName(u"scrollAreaWidgetContents_1")
        self.scrollAreaWidgetContents_1.setGeometry(QRect(0, 0, 599, 434))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents_1)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox_dir = QGroupBox(self.scrollAreaWidgetContents_1)
        self.groupBox_dir.setObjectName(u"groupBox_dir")
        self.groupBox_dir.setMinimumSize(QSize(0, 0))
        self.groupBox_dir.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_dir)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_1 = QHBoxLayout()
        self.horizontalLayout_1.setObjectName(u"horizontalLayout_1")
        self.label = QLabel(self.groupBox_dir)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(160, 0))
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_1.addWidget(self.label)

        self.lineEdit_steamPath = QLineEdit(self.groupBox_dir)
        self.lineEdit_steamPath.setObjectName(u"lineEdit_steamPath")

        self.horizontalLayout_1.addWidget(self.lineEdit_steamPath)

        self.btn_steamPath = QCommandLinkButton(self.groupBox_dir)
        self.btn_steamPath.setObjectName(u"btn_steamPath")
        self.btn_steamPath.setMaximumSize(QSize(36, 16777215))
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.SystemSearch))
        self.btn_steamPath.setIcon(icon3)
        self.btn_steamPath.setIconSize(QSize(20, 20))

        self.horizontalLayout_1.addWidget(self.btn_steamPath, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout_3.addLayout(self.horizontalLayout_1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.groupBox_dir)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(160, 0))
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineEdit_wallpaperPath = QLineEdit(self.groupBox_dir)
        self.lineEdit_wallpaperPath.setObjectName(u"lineEdit_wallpaperPath")

        self.horizontalLayout_2.addWidget(self.lineEdit_wallpaperPath)

        self.btn_wallpaperPath = QCommandLinkButton(self.groupBox_dir)
        self.btn_wallpaperPath.setObjectName(u"btn_wallpaperPath")
        self.btn_wallpaperPath.setMaximumSize(QSize(36, 16777215))
        self.btn_wallpaperPath.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.btn_wallpaperPath, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_4 = QLabel(self.groupBox_dir)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(160, 0))
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.label_4)

        self.lineEdit_wallpaperBackupPath = QLineEdit(self.groupBox_dir)
        self.lineEdit_wallpaperBackupPath.setObjectName(u"lineEdit_wallpaperBackupPath")

        self.horizontalLayout_3.addWidget(self.lineEdit_wallpaperBackupPath)

        self.btn_wallpaperBackupPath = QCommandLinkButton(self.groupBox_dir)
        self.btn_wallpaperBackupPath.setObjectName(u"btn_wallpaperBackupPath")
        self.btn_wallpaperBackupPath.setMaximumSize(QSize(36, 16777215))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setUnderline(False)
        self.btn_wallpaperBackupPath.setFont(font)
        self.btn_wallpaperBackupPath.setIcon(icon1)

        self.horizontalLayout_3.addWidget(self.btn_wallpaperBackupPath, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.verticalLayout_2.addWidget(self.groupBox_dir)

        self.groupBox = QGroupBox(self.scrollAreaWidgetContents_1)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setLineWidth(2)

        self.verticalLayout.addWidget(self.label_8)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.lineEdit_nas_path_backup = QLineEdit(self.groupBox)
        self.lineEdit_nas_path_backup.setObjectName(u"lineEdit_nas_path_backup")

        self.horizontalLayout_6.addWidget(self.lineEdit_nas_path_backup)

        self.btn_backup_nas = QPushButton(self.groupBox)
        self.btn_backup_nas.setObjectName(u"btn_backup_nas")
        self.btn_backup_nas.setMinimumSize(QSize(0, 23))

        self.horizontalLayout_6.addWidget(self.btn_backup_nas)


        self.verticalLayout.addLayout(self.horizontalLayout_6)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.groupBox_info = QGroupBox(self.scrollAreaWidgetContents_1)
        self.groupBox_info.setObjectName(u"groupBox_info")
        self.groupBox_info.setMinimumSize(QSize(0, 60))
        self.verticalLayout_6 = QVBoxLayout(self.groupBox_info)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_version = QLabel(self.groupBox_info)
        self.label_version.setObjectName(u"label_version")

        self.verticalLayout_6.addWidget(self.label_version)


        self.verticalLayout_2.addWidget(self.groupBox_info)

        self.verticalSpacer = QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.scrollArea_1.setWidget(self.scrollAreaWidgetContents_1)

        self.gridLayout_3.addWidget(self.scrollArea_1, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_set, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        QWidget.setTabOrder(self.lineEdit_steamPath, self.btn_steamPath)
        QWidget.setTabOrder(self.btn_steamPath, self.lineEdit_wallpaperPath)
        QWidget.setTabOrder(self.lineEdit_wallpaperPath, self.btn_wallpaperPath)
        QWidget.setTabOrder(self.btn_wallpaperPath, self.lineEdit_wallpaperBackupPath)
        QWidget.setTabOrder(self.lineEdit_wallpaperBackupPath, self.btn_wallpaperBackupPath)

        self.retranslateUi(MainForm)

        self.tabWidget.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(MainForm)
    # setupUi

    def retranslateUi(self, MainForm):
        MainForm.setWindowTitle(QCoreApplication.translate("MainForm", u"Wallpaper Engine Tools", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_main), QCoreApplication.translate("MainForm", u"\u5df2\u8ba2\u9605", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_backup), QCoreApplication.translate("MainForm", u"\u5907\u4efd", None))
        self.lineEdit_repkg.setPlaceholderText(QCoreApplication.translate("MainForm", u"\u62d6\u5165\u9700\u8981\u63d0\u53d6\u7684PKG/MPKG\u6587\u4ef6", None))
        self.btn_repkgPath.setText("")
        self.btn_repkg.setText(QCoreApplication.translate("MainForm", u"\u63d0\u53d6", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainForm", u"RePKG", None))
        self.label_7.setText(QCoreApplication.translate("MainForm", u"C\u76d8\u7626\u8eab\uff08mklink\u547d\u4ee4\u751f\u6210\u8f6f\u94fe\u63a5\u76ee\u5f55\u8fc1\u79fb\u9879\u76ee\uff09\n"
"\u6ce8\u610f\uff1a\u751f\u6210\u8f6f\u94fe\u63a5\u5c06\u91cd\u547d\u540d\u6e90\u6587\u4ef6\u5939\uff08\u540d\u79f0+\u540e\u7f00\uff09\u9632\u6b62\u4e22\u5931\uff0c\u5982\u679c\u5931\u8d25\u8bf7\u624b\u52a8\u6539\u56de\u3002\n"
"\u5185\u5bb9\u8f6c\u79fb\u4e0d\u5efa\u8bae\u4f7f\u7528\uff0c\u8bf7\u624b\u52a8\u526a\u5207\u8ba2\u9605\u76ee\u5f55", None))
        self.btn_mklink_new.setText(QCoreApplication.translate("MainForm", u"\u65b0\u589e", None))
        self.label_3.setText(QCoreApplication.translate("MainForm", u"\u539f\u5730\u5740\uff08\u66ff\u6362\u8f6f\u94fe\u63a5\uff09", None))
        self.lineEdit_mklink_path.setPlaceholderText(QCoreApplication.translate("MainForm", u"\u5c06\u9700\u8981\u751f\u6210\u7684\u6587\u4ef6\u5939\u62d6\u5165\u8fd9\u91cc", None))
        self.btn_mklink_open_old.setText(QCoreApplication.translate("MainForm", u"\u6253\u5f00", None))
        self.label_5.setText(QCoreApplication.translate("MainForm", u"\u76ee\u6807\u5730\u5740\uff08\u6307\u5411\u65b0\u5730\u5740\uff09", None))
        self.lineEdit_mklink_path_new.setPlaceholderText(QCoreApplication.translate("MainForm", u"\u4f8b\uff1aD:/Documents/wallpaper_engine_backup", None))
        self.btn_mklink_open.setText(QCoreApplication.translate("MainForm", u"\u6253\u5f00", None))
        self.btn_mklink_create.setText(QCoreApplication.translate("MainForm", u"\u751f\u6210\u8f6f\u94fe\u63a5\uff08\u539f\u5730\u5740->\u76ee\u6807\u5730\u5740\uff09", None))
        self.btn_mklink_restore.setText(QCoreApplication.translate("MainForm", u"\u8fd8\u539f", None))
        self.btn_dir_move.setText(QCoreApplication.translate("MainForm", u"\u5185\u5bb9\u8f6c\u79fb", None))
        self.btn_mklink_remove.setText(QCoreApplication.translate("MainForm", u"\u79fb\u9664", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_mklink), QCoreApplication.translate("MainForm", u"Mklink", None))
        self.groupBox_dir.setTitle(QCoreApplication.translate("MainForm", u"\u8f6f\u4ef6\u76ee\u5f55", None))
        self.label.setText(QCoreApplication.translate("MainForm", u"Steam\u5b89\u88c5\u4f4d\u7f6e", None))
        self.lineEdit_steamPath.setPlaceholderText(QCoreApplication.translate("MainForm", u"\u4f8b\uff1aC:\\Program Files (x86)\\Steam", None))
        self.btn_steamPath.setText("")
        self.label_2.setText(QCoreApplication.translate("MainForm", u"wallpaper engine\u5b89\u88c5\u4f4d\u7f6e", None))
        self.lineEdit_wallpaperPath.setPlaceholderText(QCoreApplication.translate("MainForm", u"\u4f8b\uff1aC:\\Program Files (x86)\\Steam\\steamapps\\common\\wallpaper_engine", None))
        self.btn_wallpaperPath.setText("")
        self.label_4.setText(QCoreApplication.translate("MainForm", u"\u5907\u4efd\u4f4d\u7f6e", None))
        self.lineEdit_wallpaperBackupPath.setPlaceholderText(QCoreApplication.translate("MainForm", u"\u4f8b\uff1aC:\\Program Files (x86)\\Steam\\steamapps\\common\\wallpaper_engine\\projects\\backup", None))
        self.btn_wallpaperBackupPath.setText("")
        self.groupBox.setTitle(QCoreApplication.translate("MainForm", u"NAS\u5907\u4efd", None))
        self.label_8.setText(QCoreApplication.translate("MainForm", u"\u9488\u5bf9\u4e0d\u5e38\u7528\u58c1\u7eb8\u548c\u5e94\u7528\u538b\u7f29\u5305\u8fc1\u79fb\u6765\u51cf\u5c0f\u786c\u76d8\u5360\u7528\n"
"\u6b65\u9aa4\uff1a1.\u624b\u52a8\u8f6c\u79fb\u9879\u76ee\u5230\u6307\u5b9aip\u5730\u5740\u76ee\u5f55 2.\u751f\u6210\u5feb\u6377\u65b9\u5f0f", None))
        self.lineEdit_nas_path_backup.setPlaceholderText(QCoreApplication.translate("MainForm", u"ip\u5730\u5740\uff1aftp://192.168.10.101/wallpaper_engine", None))
        self.btn_backup_nas.setText(QCoreApplication.translate("MainForm", u"\u751f\u6210\u5feb\u6377\u65b9\u5f0f", None))
        self.groupBox_info.setTitle(QCoreApplication.translate("MainForm", u"\u5173\u4e8e", None))
        self.label_version.setText(QCoreApplication.translate("MainForm", u"\u7248\u672c\uff1a0", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_set), QCoreApplication.translate("MainForm", u"\u8bbe\u7f6e", None))
    # retranslateUi

