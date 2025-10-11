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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QButtonGroup, QCheckBox,
    QComboBox, QCommandLinkButton, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QProgressBar,
    QPushButton, QRadioButton, QScrollArea, QSizePolicy,
    QSpacerItem, QTabWidget, QTableWidget, QTableWidgetItem,
    QToolButton, QVBoxLayout, QWidget)

class Ui_MainForm(object):
    def setupUi(self, MainForm):
        if not MainForm.objectName():
            MainForm.setObjectName(u"MainForm")
        MainForm.setEnabled(True)
        MainForm.resize(1024, 768)
        MainForm.setMinimumSize(QSize(1024, 768))
        icon = QIcon()
        icon.addFile(u":/img/icon.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainForm.setWindowIcon(icon)
        self.gridLayout = QGridLayout(MainForm)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(MainForm)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_main = QWidget()
        self.tab_main.setObjectName(u"tab_main")
        self.verticalLayout_4 = QVBoxLayout(self.tab_main)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.frame = QFrame(self.tab_main)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.Panel)
        self.frame.setFrameShadow(QFrame.Shadow.Sunken)
        self.horizontalLayout_12 = QHBoxLayout(self.frame)
        self.horizontalLayout_12.setSpacing(0)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.lineEdit_search = QLineEdit(self.frame)
        self.lineEdit_search.setObjectName(u"lineEdit_search")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_search.sizePolicy().hasHeightForWidth())
        self.lineEdit_search.setSizePolicy(sizePolicy)
        self.lineEdit_search.setMinimumSize(QSize(200, 0))
        self.lineEdit_search.setFrame(False)

        self.horizontalLayout_12.addWidget(self.lineEdit_search)

        self.btn_clear = QToolButton(self.frame)
        self.btn_clear.setObjectName(u"btn_clear")
        self.btn_clear.setStyleSheet(u"border-style: outset;")
        icon1 = QIcon(QIcon.fromTheme(u"edit-clear"))
        self.btn_clear.setIcon(icon1)

        self.horizontalLayout_12.addWidget(self.btn_clear)

        self.btn_search = QToolButton(self.frame)
        self.btn_search.setObjectName(u"btn_search")
        self.btn_search.setStyleSheet(u"border-style: outset;")
        icon2 = QIcon(QIcon.fromTheme(u"edit-find"))
        self.btn_search.setIcon(icon2)

        self.horizontalLayout_12.addWidget(self.btn_search)


        self.horizontalLayout_13.addWidget(self.frame)

        self.label_filter = QLabel(self.tab_main)
        self.label_filter.setObjectName(u"label_filter")

        self.horizontalLayout_13.addWidget(self.label_filter)

        self.horizontalSpacer_4 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_4)

        self.progressBar = QProgressBar(self.tab_main)
        self.progressBar.setObjectName(u"progressBar")

        self.horizontalLayout_13.addWidget(self.progressBar)


        self.verticalLayout_4.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setSpacing(0)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(-1, -1, 9, -1)
        self.groupBox_2 = QGroupBox(self.tab_main)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.checkBox_scene = QCheckBox(self.groupBox_2)
        self.buttonGroup_type = QButtonGroup(MainForm)
        self.buttonGroup_type.setObjectName(u"buttonGroup_type")
        self.buttonGroup_type.setExclusive(False)
        self.buttonGroup_type.addButton(self.checkBox_scene)
        self.checkBox_scene.setObjectName(u"checkBox_scene")
        self.checkBox_scene.setMinimumSize(QSize(0, 0))
        self.checkBox_scene.setMaximumSize(QSize(16777215, 16777215))

        self.verticalLayout_9.addWidget(self.checkBox_scene)

        self.checkBox_video = QCheckBox(self.groupBox_2)
        self.buttonGroup_type.addButton(self.checkBox_video)
        self.checkBox_video.setObjectName(u"checkBox_video")
        self.checkBox_video.setMinimumSize(QSize(0, 0))
        self.checkBox_video.setMaximumSize(QSize(16777215, 16777215))
        self.checkBox_video.setChecked(False)

        self.verticalLayout_9.addWidget(self.checkBox_video)

        self.checkBox_web = QCheckBox(self.groupBox_2)
        self.buttonGroup_type.addButton(self.checkBox_web)
        self.checkBox_web.setObjectName(u"checkBox_web")
        self.checkBox_web.setMinimumSize(QSize(0, 0))
        self.checkBox_web.setMaximumSize(QSize(16777215, 16777215))
        self.checkBox_web.setChecked(False)

        self.verticalLayout_9.addWidget(self.checkBox_web)

        self.checkBox_application = QCheckBox(self.groupBox_2)
        self.buttonGroup_type.addButton(self.checkBox_application)
        self.checkBox_application.setObjectName(u"checkBox_application")
        self.checkBox_application.setMinimumSize(QSize(0, 0))
        self.checkBox_application.setMaximumSize(QSize(16777215, 16777215))
        self.checkBox_application.setChecked(False)

        self.verticalLayout_9.addWidget(self.checkBox_application)


        self.verticalLayout_8.addWidget(self.groupBox_2)

        self.groupBox_4 = QGroupBox(self.tab_main)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.verticalLayout_10 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.checkBox_wallpaper = QCheckBox(self.groupBox_4)
        self.buttonGroup_source = QButtonGroup(MainForm)
        self.buttonGroup_source.setObjectName(u"buttonGroup_source")
        self.buttonGroup_source.setExclusive(False)
        self.buttonGroup_source.addButton(self.checkBox_wallpaper)
        self.checkBox_wallpaper.setObjectName(u"checkBox_wallpaper")

        self.verticalLayout_10.addWidget(self.checkBox_wallpaper)

        self.checkBox_backup = QCheckBox(self.groupBox_4)
        self.buttonGroup_source.addButton(self.checkBox_backup)
        self.checkBox_backup.setObjectName(u"checkBox_backup")

        self.verticalLayout_10.addWidget(self.checkBox_backup)

        self.checkBox_invalid = QCheckBox(self.groupBox_4)
        self.buttonGroup_source.addButton(self.checkBox_invalid)
        self.checkBox_invalid.setObjectName(u"checkBox_invalid")
        self.checkBox_invalid.setMinimumSize(QSize(0, 0))
        self.checkBox_invalid.setMaximumSize(QSize(16777215, 16777215))

        self.verticalLayout_10.addWidget(self.checkBox_invalid)

        self.checkBox_temp = QCheckBox(self.groupBox_4)
        self.buttonGroup_source.addButton(self.checkBox_temp)
        self.checkBox_temp.setObjectName(u"checkBox_temp")

        self.verticalLayout_10.addWidget(self.checkBox_temp)


        self.verticalLayout_8.addWidget(self.groupBox_4)

        self.groupBox_7 = QGroupBox(self.tab_main)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.verticalLayout_16 = QVBoxLayout(self.groupBox_7)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.comboBox_sort = QComboBox(self.groupBox_7)
        self.comboBox_sort.addItem("")
        self.comboBox_sort.addItem("")
        self.comboBox_sort.addItem("")
        self.comboBox_sort.addItem("")
        self.comboBox_sort.addItem("")
        self.comboBox_sort.addItem("")
        self.comboBox_sort.setObjectName(u"comboBox_sort")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_sort.sizePolicy().hasHeightForWidth())
        self.comboBox_sort.setSizePolicy(sizePolicy1)

        self.verticalLayout_16.addWidget(self.comboBox_sort)

        self.radioButton_positive = QRadioButton(self.groupBox_7)
        self.buttonGroup_sort = QButtonGroup(MainForm)
        self.buttonGroup_sort.setObjectName(u"buttonGroup_sort")
        self.buttonGroup_sort.addButton(self.radioButton_positive)
        self.radioButton_positive.setObjectName(u"radioButton_positive")
        self.radioButton_positive.setChecked(True)

        self.verticalLayout_16.addWidget(self.radioButton_positive)

        self.radioButton_reverse = QRadioButton(self.groupBox_7)
        self.buttonGroup_sort.addButton(self.radioButton_reverse)
        self.radioButton_reverse.setObjectName(u"radioButton_reverse")

        self.verticalLayout_16.addWidget(self.radioButton_reverse)


        self.verticalLayout_8.addWidget(self.groupBox_7)

        self.groupBox_5 = QGroupBox(self.tab_main)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.verticalLayout_14 = QVBoxLayout(self.groupBox_5)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.radioButton_big = QRadioButton(self.groupBox_5)
        self.buttonGroup_img = QButtonGroup(MainForm)
        self.buttonGroup_img.setObjectName(u"buttonGroup_img")
        self.buttonGroup_img.addButton(self.radioButton_big)
        self.radioButton_big.setObjectName(u"radioButton_big")

        self.verticalLayout_14.addWidget(self.radioButton_big)

        self.radioButton_small = QRadioButton(self.groupBox_5)
        self.buttonGroup_img.addButton(self.radioButton_small)
        self.radioButton_small.setObjectName(u"radioButton_small")
        self.radioButton_small.setChecked(True)

        self.verticalLayout_14.addWidget(self.radioButton_small)

        self.label_10 = QLabel(self.groupBox_5)
        self.label_10.setObjectName(u"label_10")

        self.verticalLayout_14.addWidget(self.label_10)

        self.comboBox_size = QComboBox(self.groupBox_5)
        self.comboBox_size.addItem("")
        self.comboBox_size.addItem("")
        self.comboBox_size.addItem("")
        self.comboBox_size.addItem("")
        self.comboBox_size.setObjectName(u"comboBox_size")

        self.verticalLayout_14.addWidget(self.comboBox_size)


        self.verticalLayout_8.addWidget(self.groupBox_5)

        self.groupBox_3 = QGroupBox(self.tab_main)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_11 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.checkBox_folders = QCheckBox(self.groupBox_3)
        self.checkBox_folders.setObjectName(u"checkBox_folders")

        self.verticalLayout_11.addWidget(self.checkBox_folders)

        self.checkBox_authorblock = QCheckBox(self.groupBox_3)
        self.checkBox_authorblock.setObjectName(u"checkBox_authorblock")

        self.verticalLayout_11.addWidget(self.checkBox_authorblock)

        self.btn_invalid = QPushButton(self.groupBox_3)
        self.btn_invalid.setObjectName(u"btn_invalid")
        self.btn_invalid.setMinimumSize(QSize(0, 0))
        self.btn_invalid.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 85, 0);")
        self.btn_invalid.setCheckable(False)
        self.btn_invalid.setAutoDefault(False)
        self.btn_invalid.setFlat(False)

        self.verticalLayout_11.addWidget(self.btn_invalid)


        self.verticalLayout_8.addWidget(self.groupBox_3)

        self.verticalSpacer_2 = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_2)

        self.label_capacity = QLabel(self.tab_main)
        self.label_capacity.setObjectName(u"label_capacity")

        self.verticalLayout_8.addWidget(self.label_capacity)


        self.horizontalLayout_14.addLayout(self.verticalLayout_8)

        self.verticalLayout_main = QVBoxLayout()
        self.verticalLayout_main.setSpacing(0)
        self.verticalLayout_main.setObjectName(u"verticalLayout_main")
        self.verticalLayout_main.setContentsMargins(-1, 9, -1, -1)
        self.tableWidget_main = QTableWidget(self.tab_main)
        self.tableWidget_main.setObjectName(u"tableWidget_main")
        self.tableWidget_main.setMinimumSize(QSize(660, 0))
        self.tableWidget_main.setFrameShape(QFrame.Shape.NoFrame)
        self.tableWidget_main.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.tableWidget_main.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableWidget_main.setShowGrid(False)
        self.tableWidget_main.horizontalHeader().setVisible(False)
        self.tableWidget_main.verticalHeader().setVisible(False)

        self.verticalLayout_main.addWidget(self.tableWidget_main)

        self.label_error = QLabel(self.tab_main)
        self.label_error.setObjectName(u"label_error")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_error.sizePolicy().hasHeightForWidth())
        self.label_error.setSizePolicy(sizePolicy2)
        font = QFont()
        font.setPointSize(20)
        font.setBold(False)
        self.label_error.setFont(font)
        self.label_error.setScaledContents(False)
        self.label_error.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_main.addWidget(self.label_error)

        self.horizontalLayout_page = QHBoxLayout()
        self.horizontalLayout_page.setObjectName(u"horizontalLayout_page")
        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_page.addItem(self.horizontalSpacer)

        self.btn_left = QToolButton(self.tab_main)
        self.buttonGroup_page = QButtonGroup(MainForm)
        self.buttonGroup_page.setObjectName(u"buttonGroup_page")
        self.buttonGroup_page.setExclusive(False)
        self.buttonGroup_page.addButton(self.btn_left)
        self.btn_left.setObjectName(u"btn_left")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.btn_left.sizePolicy().hasHeightForWidth())
        self.btn_left.setSizePolicy(sizePolicy3)
        self.btn_left.setPopupMode(QToolButton.ToolButtonPopupMode.DelayedPopup)
        self.btn_left.setArrowType(Qt.ArrowType.LeftArrow)

        self.horizontalLayout_page.addWidget(self.btn_left)

        self.comboBox_page = QComboBox(self.tab_main)
        self.comboBox_page.setObjectName(u"comboBox_page")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.comboBox_page.sizePolicy().hasHeightForWidth())
        self.comboBox_page.setSizePolicy(sizePolicy4)

        self.horizontalLayout_page.addWidget(self.comboBox_page)

        self.btn_right = QToolButton(self.tab_main)
        self.buttonGroup_page.addButton(self.btn_right)
        self.btn_right.setObjectName(u"btn_right")
        sizePolicy3.setHeightForWidth(self.btn_right.sizePolicy().hasHeightForWidth())
        self.btn_right.setSizePolicy(sizePolicy3)
        self.btn_right.setArrowType(Qt.ArrowType.RightArrow)

        self.horizontalLayout_page.addWidget(self.btn_right)

        self.label_page = QLabel(self.tab_main)
        self.label_page.setObjectName(u"label_page")

        self.horizontalLayout_page.addWidget(self.label_page)

        self.horizontalSpacer_3 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_page.addItem(self.horizontalSpacer_3)


        self.verticalLayout_main.addLayout(self.horizontalLayout_page)


        self.horizontalLayout_14.addLayout(self.verticalLayout_main)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(self.tab_main)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy2.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy2)
        self.scrollArea.setMinimumSize(QSize(209, 0))
        self.scrollArea.setMaximumSize(QSize(209, 16777215))
        self.scrollArea.setAutoFillBackground(False)
        self.scrollArea.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Shadow.Plain)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 209, 549))
        self.verticalLayout_15 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(-1, -1, 0, 0)
        self.label_img = QLabel(self.scrollAreaWidgetContents)
        self.label_img.setObjectName(u"label_img")
        self.label_img.setMinimumSize(QSize(190, 190))
        self.label_img.setPixmap(QPixmap(u":/img/background-img.jpg"))
        self.label_img.setScaledContents(True)

        self.verticalLayout_15.addWidget(self.label_img)

        self.label_error_project = QLabel(self.scrollAreaWidgetContents)
        self.label_error_project.setObjectName(u"label_error_project")
        font1 = QFont()
        font1.setPointSize(14)
        self.label_error_project.setFont(font1)
        self.label_error_project.setStyleSheet(u"color: rgb(119, 119, 119);")
        self.label_error_project.setScaledContents(False)
        self.label_error_project.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_15.addWidget(self.label_error_project)

        self.label_name = QLabel(self.scrollAreaWidgetContents)
        self.label_name.setObjectName(u"label_name")
        self.label_name.setMaximumSize(QSize(200, 16777215))
        self.label_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_name.setWordWrap(True)

        self.verticalLayout_15.addWidget(self.label_name)

        self.label_title = QLabel(self.scrollAreaWidgetContents)
        self.label_title.setObjectName(u"label_title")
        self.label_title.setMaximumSize(QSize(200, 16777215))
        font2 = QFont()
        font2.setPointSize(11)
        self.label_title.setFont(font2)
        self.label_title.setWordWrap(True)

        self.verticalLayout_15.addWidget(self.label_title)

        self.label_type = QLabel(self.scrollAreaWidgetContents)
        self.label_type.setObjectName(u"label_type")
        self.label_type.setMaximumSize(QSize(200, 16777215))
        self.label_type.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_15.addWidget(self.label_type)

        self.label_subscriptiondate = QLabel(self.scrollAreaWidgetContents)
        self.label_subscriptiondate.setObjectName(u"label_subscriptiondate")
        self.label_subscriptiondate.setMaximumSize(QSize(200, 16777215))
        font3 = QFont()
        font3.setPointSize(9)
        font3.setWeight(QFont.Light)
        self.label_subscriptiondate.setFont(font3)
        self.label_subscriptiondate.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_subscriptiondate.setWordWrap(True)

        self.verticalLayout_15.addWidget(self.label_subscriptiondate)

        self.label_updatedate = QLabel(self.scrollAreaWidgetContents)
        self.label_updatedate.setObjectName(u"label_updatedate")
        self.label_updatedate.setMaximumSize(QSize(200, 16777215))
        font4 = QFont()
        font4.setWeight(QFont.Light)
        self.label_updatedate.setFont(font4)
        self.label_updatedate.setFrameShape(QFrame.Shape.NoFrame)
        self.label_updatedate.setFrameShadow(QFrame.Shadow.Plain)
        self.label_updatedate.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_updatedate.setWordWrap(True)

        self.verticalLayout_15.addWidget(self.label_updatedate)

        self.label_note = QLabel(self.scrollAreaWidgetContents)
        self.label_note.setObjectName(u"label_note")
        self.label_note.setMaximumSize(QSize(200, 16777215))
        self.label_note.setWordWrap(True)

        self.verticalLayout_15.addWidget(self.label_note)

        self.verticalSpacer_3 = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_3)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.groupBox_btn = QGroupBox(self.tab_main)
        self.groupBox_btn.setObjectName(u"groupBox_btn")
        self.verticalLayout_13 = QVBoxLayout(self.groupBox_btn)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.btn_open = QPushButton(self.groupBox_btn)
        self.btn_open.setObjectName(u"btn_open")
        self.btn_open.setMinimumSize(QSize(0, 0))
        self.btn_open.setMaximumSize(QSize(16777215, 16777215))
        self.btn_open.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(85, 170, 255);")

        self.verticalLayout_13.addWidget(self.btn_open)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.btn_edit = QPushButton(self.groupBox_btn)
        self.btn_edit.setObjectName(u"btn_edit")
        self.btn_edit.setMinimumSize(QSize(0, 0))
        self.btn_edit.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_15.addWidget(self.btn_edit)

        self.btn_capacity = QPushButton(self.groupBox_btn)
        self.btn_capacity.setObjectName(u"btn_capacity")

        self.horizontalLayout_15.addWidget(self.btn_capacity)


        self.verticalLayout_13.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.btn_repkg_work = QPushButton(self.groupBox_btn)
        self.btn_repkg_work.setObjectName(u"btn_repkg_work")
        self.btn_repkg_work.setMinimumSize(QSize(0, 0))

        self.horizontalLayout_16.addWidget(self.btn_repkg_work)

        self.btn_repkg_dir = QPushButton(self.groupBox_btn)
        self.btn_repkg_dir.setObjectName(u"btn_repkg_dir")
        self.btn_repkg_dir.setMinimumSize(QSize(0, 0))

        self.horizontalLayout_16.addWidget(self.btn_repkg_dir)


        self.verticalLayout_13.addLayout(self.horizontalLayout_16)


        self.verticalLayout.addWidget(self.groupBox_btn)


        self.horizontalLayout_14.addLayout(self.verticalLayout)


        self.verticalLayout_4.addLayout(self.horizontalLayout_14)

        self.tabWidget.addTab(self.tab_main, "")
        self.tab_repkg = QWidget()
        self.tab_repkg.setObjectName(u"tab_repkg")
        self.verticalLayout_5 = QVBoxLayout(self.tab_repkg)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.lineEdit_repkg = QLineEdit(self.tab_repkg)
        self.lineEdit_repkg.setObjectName(u"lineEdit_repkg")

        self.horizontalLayout_8.addWidget(self.lineEdit_repkg)

        self.btn_repkgPath = QPushButton(self.tab_repkg)
        self.btn_repkgPath.setObjectName(u"btn_repkgPath")
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditFind))
        self.btn_repkgPath.setIcon(icon3)

        self.horizontalLayout_8.addWidget(self.btn_repkgPath)

        self.btn_repkg = QPushButton(self.tab_repkg)
        self.btn_repkg.setObjectName(u"btn_repkg")
        self.btn_repkg.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(85, 170, 255);")

        self.horizontalLayout_8.addWidget(self.btn_repkg)

        self.btn_repkg_output = QPushButton(self.tab_repkg)
        self.btn_repkg_output.setObjectName(u"btn_repkg_output")
        self.btn_repkg_output.setMinimumSize(QSize(0, 0))

        self.horizontalLayout_8.addWidget(self.btn_repkg_output)


        self.verticalLayout_5.addLayout(self.horizontalLayout_8)

        self.tableWidget_repkg = QTableWidget(self.tab_repkg)
        if (self.tableWidget_repkg.columnCount() < 4):
            self.tableWidget_repkg.setColumnCount(4)
        self.tableWidget_repkg.setObjectName(u"tableWidget_repkg")
        self.tableWidget_repkg.setMinimumSize(QSize(982, 0))
        self.tableWidget_repkg.setFrameShape(QFrame.Shape.NoFrame)
        self.tableWidget_repkg.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.tableWidget_repkg.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableWidget_repkg.setColumnCount(4)
        self.tableWidget_repkg.horizontalHeader().setVisible(False)
        self.tableWidget_repkg.verticalHeader().setVisible(False)

        self.verticalLayout_5.addWidget(self.tableWidget_repkg)

        self.tabWidget.addTab(self.tab_repkg, "")
        self.tab_mklink = QWidget()
        self.tab_mklink.setObjectName(u"tab_mklink")
        self.verticalLayout_7 = QVBoxLayout(self.tab_mklink)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.groupBox_10 = QGroupBox(self.tab_mklink)
        self.groupBox_10.setObjectName(u"groupBox_10")
        self.horizontalLayout_20 = QHBoxLayout(self.groupBox_10)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.label_7 = QLabel(self.groupBox_10)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(180, 0))
        self.label_7.setMaximumSize(QSize(180, 16777215))
        self.label_7.setLineWidth(2)
        self.label_7.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.label_7.setWordWrap(True)

        self.horizontalLayout_20.addWidget(self.label_7)

        self.verticalLayout_20 = QVBoxLayout()
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_3 = QLabel(self.groupBox_10)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(160, 0))
        self.label_3.setMaximumSize(QSize(160, 16777215))
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.label_3)

        self.lineEdit_mklink_path = QLineEdit(self.groupBox_10)
        self.lineEdit_mklink_path.setObjectName(u"lineEdit_mklink_path")
        self.lineEdit_mklink_path.setEnabled(False)

        self.horizontalLayout_5.addWidget(self.lineEdit_mklink_path)

        self.btn_mklink_open_old = QPushButton(self.groupBox_10)
        self.btn_mklink_open_old.setObjectName(u"btn_mklink_open_old")
        self.btn_mklink_open_old.setMaximumSize(QSize(48, 16777215))

        self.horizontalLayout_5.addWidget(self.btn_mklink_open_old)


        self.verticalLayout_20.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_5 = QLabel(self.groupBox_10)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(160, 0))
        self.label_5.setMaximumSize(QSize(160, 16777215))
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_7.addWidget(self.label_5)

        self.lineEdit_mklink_path_new = QLineEdit(self.groupBox_10)
        self.lineEdit_mklink_path_new.setObjectName(u"lineEdit_mklink_path_new")

        self.horizontalLayout_7.addWidget(self.lineEdit_mklink_path_new)

        self.btn_mklink_open = QPushButton(self.groupBox_10)
        self.btn_mklink_open.setObjectName(u"btn_mklink_open")
        self.btn_mklink_open.setMaximumSize(QSize(48, 16777215))

        self.horizontalLayout_7.addWidget(self.btn_mklink_open)


        self.verticalLayout_20.addLayout(self.horizontalLayout_7)

        self.listWidget_mklink = QListWidget(self.groupBox_10)
        self.listWidget_mklink.setObjectName(u"listWidget_mklink")
        self.listWidget_mklink.setSpacing(6)

        self.verticalLayout_20.addWidget(self.listWidget_mklink)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.btn_mklink_new = QPushButton(self.groupBox_10)
        self.btn_mklink_new.setObjectName(u"btn_mklink_new")
        self.btn_mklink_new.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(85, 170, 255);")

        self.horizontalLayout.addWidget(self.btn_mklink_new)

        self.btn_mklink_remove = QPushButton(self.groupBox_10)
        self.btn_mklink_remove.setObjectName(u"btn_mklink_remove")
        self.btn_mklink_remove.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 85, 0);")

        self.horizontalLayout.addWidget(self.btn_mklink_remove)

        self.btn_mklink_create = QPushButton(self.groupBox_10)
        self.btn_mklink_create.setObjectName(u"btn_mklink_create")
        self.btn_mklink_create.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(85, 85, 255);")

        self.horizontalLayout.addWidget(self.btn_mklink_create)

        self.btn_mklink_restore = QPushButton(self.groupBox_10)
        self.btn_mklink_restore.setObjectName(u"btn_mklink_restore")
        self.btn_mklink_restore.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 170, 127);")

        self.horizontalLayout.addWidget(self.btn_mklink_restore)


        self.verticalLayout_20.addLayout(self.horizontalLayout)


        self.horizontalLayout_20.addLayout(self.verticalLayout_20)


        self.verticalLayout_7.addWidget(self.groupBox_10)

        self.groupBox_9 = QGroupBox(self.tab_mklink)
        self.groupBox_9.setObjectName(u"groupBox_9")
        self.horizontalLayout_19 = QHBoxLayout(self.groupBox_9)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.label_8 = QLabel(self.groupBox_9)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMinimumSize(QSize(180, 0))
        self.label_8.setMaximumSize(QSize(180, 16777215))
        self.label_8.setLineWidth(2)
        self.label_8.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.label_8.setWordWrap(True)

        self.horizontalLayout_19.addWidget(self.label_8)

        self.verticalLayout_19 = QVBoxLayout()
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_6 = QLabel(self.groupBox_9)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_6.addWidget(self.label_6)

        self.lineEdit_nas_path_backup = QLineEdit(self.groupBox_9)
        self.lineEdit_nas_path_backup.setObjectName(u"lineEdit_nas_path_backup")
        self.lineEdit_nas_path_backup.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_6.addWidget(self.lineEdit_nas_path_backup)

        self.btn_nas_save = QPushButton(self.groupBox_9)
        self.btn_nas_save.setObjectName(u"btn_nas_save")

        self.horizontalLayout_6.addWidget(self.btn_nas_save)

        self.btn_naslink_new = QPushButton(self.groupBox_9)
        self.btn_naslink_new.setObjectName(u"btn_naslink_new")
        self.btn_naslink_new.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(85, 170, 255);")

        self.horizontalLayout_6.addWidget(self.btn_naslink_new)

        self.btn_naslink_remove = QPushButton(self.groupBox_9)
        self.btn_naslink_remove.setObjectName(u"btn_naslink_remove")
        self.btn_naslink_remove.setMaximumSize(QSize(80, 16777215))
        self.btn_naslink_remove.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 85, 0);")

        self.horizontalLayout_6.addWidget(self.btn_naslink_remove)

        self.btn_naslink_create = QPushButton(self.groupBox_9)
        self.btn_naslink_create.setObjectName(u"btn_naslink_create")
        self.btn_naslink_create.setMinimumSize(QSize(120, 23))
        self.btn_naslink_create.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(85, 85, 255);")

        self.horizontalLayout_6.addWidget(self.btn_naslink_create)


        self.verticalLayout_19.addLayout(self.horizontalLayout_6)

        self.listWidget_nas = QListWidget(self.groupBox_9)
        self.listWidget_nas.setObjectName(u"listWidget_nas")
        self.listWidget_nas.setSpacing(2)

        self.verticalLayout_19.addWidget(self.listWidget_nas)


        self.horizontalLayout_19.addLayout(self.verticalLayout_19)


        self.verticalLayout_7.addWidget(self.groupBox_9)

        self.groupBox_11 = QGroupBox(self.tab_mklink)
        self.groupBox_11.setObjectName(u"groupBox_11")
        self.verticalLayout_21 = QVBoxLayout(self.groupBox_11)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_5)

        self.btn_temp_new = QPushButton(self.groupBox_11)
        self.btn_temp_new.setObjectName(u"btn_temp_new")
        self.btn_temp_new.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(85, 170, 255);")

        self.horizontalLayout_4.addWidget(self.btn_temp_new)

        self.btn_temp_remove = QPushButton(self.groupBox_11)
        self.btn_temp_remove.setObjectName(u"btn_temp_remove")
        self.btn_temp_remove.setMaximumSize(QSize(80, 16777215))
        self.btn_temp_remove.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 85, 0);")

        self.horizontalLayout_4.addWidget(self.btn_temp_remove)


        self.verticalLayout_21.addLayout(self.horizontalLayout_4)

        self.listWidget_temp = QListWidget(self.groupBox_11)
        self.listWidget_temp.setObjectName(u"listWidget_temp")

        self.verticalLayout_21.addWidget(self.listWidget_temp)


        self.verticalLayout_7.addWidget(self.groupBox_11)

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
        self.scrollAreaWidgetContents_1.setGeometry(QRect(0, 0, 983, 782))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents_1)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox_dir = QGroupBox(self.scrollAreaWidgetContents_1)
        self.groupBox_dir.setObjectName(u"groupBox_dir")
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
        icon4 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.SystemSearch))
        self.btn_steamPath.setIcon(icon4)
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
        self.btn_wallpaperPath.setIcon(icon3)

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
        font5 = QFont()
        font5.setFamilies([u"Segoe UI"])
        font5.setUnderline(False)
        self.btn_wallpaperBackupPath.setFont(font5)
        self.btn_wallpaperBackupPath.setIcon(icon3)

        self.horizontalLayout_3.addWidget(self.btn_wallpaperBackupPath, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.verticalLayout_2.addWidget(self.groupBox_dir)

        self.groupBox_6 = QGroupBox(self.scrollAreaWidgetContents_1)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.horizontalLayout_9 = QHBoxLayout(self.groupBox_6)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.listWidget_authorblock = QListWidget(self.groupBox_6)
        self.listWidget_authorblock.setObjectName(u"listWidget_authorblock")
        self.listWidget_authorblock.setMinimumSize(QSize(0, 250))
        self.listWidget_authorblock.setFrameShape(QFrame.Shape.StyledPanel)
        self.listWidget_authorblock.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.listWidget_authorblock.setSpacing(4)

        self.verticalLayout_12.addWidget(self.listWidget_authorblock)

        self.label_12 = QLabel(self.groupBox_6)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setMinimumSize(QSize(0, 28))

        self.verticalLayout_12.addWidget(self.label_12)


        self.horizontalLayout_9.addLayout(self.verticalLayout_12)

        self.verticalLayout_18 = QVBoxLayout()
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.listWidget_virus = QListWidget(self.groupBox_6)
        self.listWidget_virus.setObjectName(u"listWidget_virus")
        self.listWidget_virus.setMinimumSize(QSize(0, 250))
        self.listWidget_virus.setSpacing(2)

        self.verticalLayout_18.addWidget(self.listWidget_virus)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.btn_virus_label = QPushButton(self.groupBox_6)
        self.btn_virus_label.setObjectName(u"btn_virus_label")
        self.btn_virus_label.setStyleSheet(u"border-style: outset;")

        self.horizontalLayout_17.addWidget(self.btn_virus_label)

        self.btn_virus_new = QPushButton(self.groupBox_6)
        self.btn_virus_new.setObjectName(u"btn_virus_new")

        self.horizontalLayout_17.addWidget(self.btn_virus_new)

        self.btn_virus_refresh = QPushButton(self.groupBox_6)
        self.btn_virus_refresh.setObjectName(u"btn_virus_refresh")

        self.horizontalLayout_17.addWidget(self.btn_virus_refresh)


        self.verticalLayout_18.addLayout(self.horizontalLayout_17)


        self.horizontalLayout_9.addLayout(self.verticalLayout_18)


        self.verticalLayout_2.addWidget(self.groupBox_6)

        self.groupBox_8 = QGroupBox(self.scrollAreaWidgetContents_1)
        self.groupBox_8.setObjectName(u"groupBox_8")
        self.verticalLayout_17 = QVBoxLayout(self.groupBox_8)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.label_11 = QLabel(self.groupBox_8)
        self.label_11.setObjectName(u"label_11")

        self.verticalLayout_17.addWidget(self.label_11)

        self.btn_restart = QPushButton(self.groupBox_8)
        self.btn_restart.setObjectName(u"btn_restart")
        self.btn_restart.setMaximumSize(QSize(200, 16777215))
        self.btn_restart.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 85, 0);")
        self.btn_restart.setCheckable(False)
        self.btn_restart.setAutoDefault(False)
        self.btn_restart.setFlat(False)

        self.verticalLayout_17.addWidget(self.btn_restart)


        self.verticalLayout_2.addWidget(self.groupBox_8)

        self.groupBox = QGroupBox(self.scrollAreaWidgetContents_1)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMinimumSize(QSize(0, 80))
        self.gridLayout_6 = QGridLayout(self.groupBox)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_11.addWidget(self.label_9)

        self.btn_unlock_hidden_achievements = QPushButton(self.groupBox)
        self.btn_unlock_hidden_achievements.setObjectName(u"btn_unlock_hidden_achievements")
        self.btn_unlock_hidden_achievements.setMaximumSize(QSize(80, 16777215))
        self.btn_unlock_hidden_achievements.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(85, 170, 255);")

        self.horizontalLayout_11.addWidget(self.btn_unlock_hidden_achievements)


        self.gridLayout_6.addLayout(self.horizontalLayout_11, 0, 0, 1, 1)


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

        self.tabWidget.setCurrentIndex(0)
        self.btn_invalid.setDefault(False)
        self.btn_restart.setDefault(False)


        QMetaObject.connectSlotsByName(MainForm)
    # setupUi

    def retranslateUi(self, MainForm):
        MainForm.setWindowTitle(QCoreApplication.translate("MainForm", u"Wallpaper Engine Tools", None))
        self.lineEdit_search.setText("")
        self.lineEdit_search.setPlaceholderText(QCoreApplication.translate("MainForm", u"\u641c\u7d22", None))
        self.label_filter.setText(QCoreApplication.translate("MainForm", u"\u7b5b\u9009\u7ed3\u679c\uff08 0 \u4e2a\u4e2d\u6709 0 \u4e2a\uff09", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainForm", u"\u7c7b\u578b", None))
        self.checkBox_scene.setText(QCoreApplication.translate("MainForm", u"\u573a\u666f", None))
        self.checkBox_video.setText(QCoreApplication.translate("MainForm", u"\u89c6\u9891", None))
        self.checkBox_web.setText(QCoreApplication.translate("MainForm", u"\u7f51\u9875", None))
        self.checkBox_application.setText(QCoreApplication.translate("MainForm", u"\u5e94\u7528", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainForm", u"\u6765\u6e90", None))
        self.checkBox_wallpaper.setText(QCoreApplication.translate("MainForm", u"\u521b\u610f\u5de5\u574a", None))
        self.checkBox_backup.setText(QCoreApplication.translate("MainForm", u"\u6211\u7684\u58c1\u7eb8", None))
        self.checkBox_invalid.setText(QCoreApplication.translate("MainForm", u"\u5931\u6548", None))
        self.checkBox_temp.setText(QCoreApplication.translate("MainForm", u"\u4e34\u65f6\u5b58\u653e", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("MainForm", u"\u6392\u5e8f", None))
        self.comboBox_sort.setItemText(0, QCoreApplication.translate("MainForm", u"\u540d\u79f0", None))
        self.comboBox_sort.setItemText(1, QCoreApplication.translate("MainForm", u"\u8bc4\u7ea7", None))
        self.comboBox_sort.setItemText(2, QCoreApplication.translate("MainForm", u"\u6536\u85cf", None))
        self.comboBox_sort.setItemText(3, QCoreApplication.translate("MainForm", u"\u6587\u4ef6\u5927\u5c0f", None))
        self.comboBox_sort.setItemText(4, QCoreApplication.translate("MainForm", u"\u8ba2\u9605\u65e5\u671f", None))
        self.comboBox_sort.setItemText(5, QCoreApplication.translate("MainForm", u"\u6700\u8fd1\u66f4\u65b0", None))

        self.radioButton_positive.setText(QCoreApplication.translate("MainForm", u"\u6b63\u5e8f", None))
        self.radioButton_reverse.setText(QCoreApplication.translate("MainForm", u"\u5012\u53d9", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainForm", u"\u67e5\u770b", None))
        self.radioButton_big.setText(QCoreApplication.translate("MainForm", u"\u5927\u56fe\u6807", None))
        self.radioButton_small.setText(QCoreApplication.translate("MainForm", u"\u5c0f\u56fe\u6807", None))
        self.label_10.setText(QCoreApplication.translate("MainForm", u"\u6bcf\u9875\u663e\u793a\u6570", None))
        self.comboBox_size.setItemText(0, QCoreApplication.translate("MainForm", u"10", None))
        self.comboBox_size.setItemText(1, QCoreApplication.translate("MainForm", u"20", None))
        self.comboBox_size.setItemText(2, QCoreApplication.translate("MainForm", u"30", None))
        self.comboBox_size.setItemText(3, QCoreApplication.translate("MainForm", u"50", None))

        self.groupBox_3.setTitle(QCoreApplication.translate("MainForm", u"\u64cd\u4f5c", None))
        self.checkBox_folders.setText(QCoreApplication.translate("MainForm", u"\u5de5\u574a\u5206\u7c7b", None))
        self.checkBox_authorblock.setText(QCoreApplication.translate("MainForm", u"\u6bd2\u6392\u67e5", None))
        self.btn_invalid.setText(QCoreApplication.translate("MainForm", u"\u5220\u9664\u5931\u6548\u8ba2\u9605", None))
        self.label_capacity.setText(QCoreApplication.translate("MainForm", u"\u5bb9\u91cf\uff1a0G", None))
        self.label_error.setText(QCoreApplication.translate("MainForm", u"\u60a8\u672a\u5b89\u88c5Wallpaper Engine", None))
        self.label_page.setText(QCoreApplication.translate("MainForm", u"\u5171 1 \u9875", None))
        self.label_img.setText("")
        self.label_error_project.setText(QCoreApplication.translate("MainForm", u"\u8bf7\u9009\u62e9\u4e00\u4e2a\u58c1\u7eb8", None))
        self.label_name.setText("")
        self.label_title.setText("")
        self.label_type.setText("")
        self.label_subscriptiondate.setText("")
        self.label_updatedate.setText("")
        self.label_note.setText("")
        self.groupBox_btn.setTitle(QCoreApplication.translate("MainForm", u"\u64cd\u4f5c", None))
        self.btn_open.setText(QCoreApplication.translate("MainForm", u"\u6253\u5f00\u8d44\u6e90\u7ba1\u7406\u5668", None))
        self.btn_edit.setText(QCoreApplication.translate("MainForm", u"\u4fee\u6539", None))
        self.btn_capacity.setText(QCoreApplication.translate("MainForm", u"\u91cd\u65b0\u83b7\u53d6\u5927\u5c0f", None))
        self.btn_repkg_work.setText(QCoreApplication.translate("MainForm", u"\u63d0\u53d6PKG", None))
        self.btn_repkg_dir.setText(QCoreApplication.translate("MainForm", u"\u6253\u5f00\u8f93\u51fa", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_main), QCoreApplication.translate("MainForm", u"\u58c1\u7eb8\u7ba1\u7406", None))
        self.lineEdit_repkg.setPlaceholderText(QCoreApplication.translate("MainForm", u"\u62d6\u5165\u9700\u8981\u63d0\u53d6\u7684PKG/MPKG\u6587\u4ef6", None))
        self.btn_repkgPath.setText("")
        self.btn_repkg.setText(QCoreApplication.translate("MainForm", u"\u63d0\u53d6", None))
        self.btn_repkg_output.setText(QCoreApplication.translate("MainForm", u"\u6253\u5f00\u8f93\u51fa", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_repkg), QCoreApplication.translate("MainForm", u"RePKG", None))
        self.groupBox_10.setTitle(QCoreApplication.translate("MainForm", u"Mklink", None))
        self.label_7.setText(QCoreApplication.translate("MainForm", u"C\u76d8\u7626\u8eab\uff08mklink\u547d\u4ee4\u751f\u6210\u8f6f\u94fe\u63a5\u76ee\u5f55\u8fc1\u79fb\u9879\u76ee\uff09\n"
"\n"
"\u6ce8\u610f\uff1a\n"
"\u751f\u6210\u8f6f\u94fe\u63a5\u5c06\u91cd\u547d\u540d\u6e90\u6587\u4ef6\u5939\uff08\u540d\u79f0+\u540e\u7f00\uff09\u9632\u6b62\u4e22\u5931\uff0c\u5982\u679c\u5931\u8d25\u8bf7\u624b\u52a8\u6539\u56de\u3002\n"
"\n"
"\u5185\u5bb9\u8f6c\u79fb\u4e0d\u5efa\u8bae\u4f7f\u7528\uff0c\u8bf7\u624b\u52a8\u526a\u5207\u8ba2\u9605\u76ee\u5f55", None))
        self.label_3.setText(QCoreApplication.translate("MainForm", u"\u539f\u5730\u5740\uff08\u66ff\u6362\u8f6f\u94fe\u63a5\uff09", None))
        self.lineEdit_mklink_path.setPlaceholderText("")
        self.btn_mklink_open_old.setText(QCoreApplication.translate("MainForm", u"\u6253\u5f00", None))
        self.label_5.setText(QCoreApplication.translate("MainForm", u"\u76ee\u6807\u5730\u5740\uff08\u6307\u5411\u65b0\u5730\u5740\uff09", None))
        self.lineEdit_mklink_path_new.setPlaceholderText(QCoreApplication.translate("MainForm", u"\u4f8b\uff1aD:/Documents/wallpaper_engine_backup", None))
        self.btn_mklink_open.setText(QCoreApplication.translate("MainForm", u"\u6253\u5f00", None))
        self.btn_mklink_new.setText(QCoreApplication.translate("MainForm", u"\u65b0\u589e", None))
        self.btn_mklink_remove.setText(QCoreApplication.translate("MainForm", u"\u79fb\u9664", None))
        self.btn_mklink_create.setText(QCoreApplication.translate("MainForm", u"\u751f\u6210\u8f6f\u94fe\u63a5\uff08\u539f\u5730\u5740->\u76ee\u6807\u5730\u5740\uff09", None))
        self.btn_mklink_restore.setText(QCoreApplication.translate("MainForm", u"\u8fd8\u539f", None))
        self.groupBox_9.setTitle(QCoreApplication.translate("MainForm", u"\u8fc1\u79fb\u5916\u7f6e\u5b58\u50a8\u4f4d\u7f6e", None))
        self.label_8.setText(QCoreApplication.translate("MainForm", u"\u9488\u5bf9\u4e0d\u5e38\u7528\u58c1\u7eb8\u548c\u5e94\u7528\u538b\u7f29\u5305\u8fc1\u79fb\u81f3NAS(\u6216\u8005\u5916\u7f6e\u786c\u76d8)\u6765\u51cf\u5c0f\u786c\u76d8\u5360\u7528\uff0c\u642d\u914d\u5feb\u6377\u65b9\u5f0f\u5feb\u901f\u5b9a\u4f4d\u6e90\u6587\u4ef6\n"
"\n"
"\u6b65\u9aa4\uff1a\n"
"1.\u58c1\u7eb8\u53f3\u952e\u624b\u52a8\u8f6c\u79fb\u9879\u76ee\u5230\u6307\u5b9aip\u5730\u5740\u76ee\u5f55 \n"
"2.\u751f\u6210\u5feb\u6377\u65b9\u5f0f\n"
"\n"
"\u6ce8\uff1a\n"
"NAS\u4e00\u4e9b\u64cd\u4f5c\u7528\u76d8\u7b26\u8df3\u8f6c\u4f1a\u51fa\u9519", None))
        self.label_6.setText(QCoreApplication.translate("MainForm", u"ip\u5730\u5740\u6216\u76d8\u7b26\uff1a", None))
        self.lineEdit_nas_path_backup.setPlaceholderText(QCoreApplication.translate("MainForm", u"ftp://112.168.217.73 \u6216\u4f7f\u7528\u5916\u7f6e\u786c\u76d8\u76d8\u7b26\uff08H:/\uff09", None))
        self.btn_nas_save.setText(QCoreApplication.translate("MainForm", u"\u4fdd\u5b58", None))
        self.btn_naslink_new.setText(QCoreApplication.translate("MainForm", u"\u65b0\u589e", None))
        self.btn_naslink_remove.setText(QCoreApplication.translate("MainForm", u"\u79fb\u9664", None))
        self.btn_naslink_create.setText(QCoreApplication.translate("MainForm", u"\u6279\u91cf\u751f\u6210\u5feb\u6377\u65b9\u5f0f", None))
        self.groupBox_11.setTitle(QCoreApplication.translate("MainForm", u"\u4e34\u65f6\u5b58\u653e", None))
        self.btn_temp_new.setText(QCoreApplication.translate("MainForm", u"\u65b0\u589e", None))
        self.btn_temp_remove.setText(QCoreApplication.translate("MainForm", u"\u79fb\u9664", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_mklink), QCoreApplication.translate("MainForm", u"\u5b58\u50a8\u6574\u7406", None))
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
        self.groupBox_6.setTitle(QCoreApplication.translate("MainForm", u"\u963b\u6b62\u540d\u5355/\u9ed1\u540d\u5355", None))
        self.label_12.setText(QCoreApplication.translate("MainForm", u"\u5de5\u574a\u53f3\u952e\n"
" - \u62a5\u544a\u963b\u6b62\u540d\u5355\n"
"", None))
        self.btn_virus_label.setText(QCoreApplication.translate("MainForm", u"\u67e5\u8be2\u6bd2\u72d7\u7684\u7f51\u5740(\u70b9\u51fb\u590d\u5236):\n"
"https://zhizhuzi.0d000721.cc/\n"
"\u6765\u6e90\uff1a\u8718\u86db\u5b50\u58c1\u7eb8\u5f15\u64ce\u81ea\u68c0\u7ec4", None))
        self.btn_virus_new.setText(QCoreApplication.translate("MainForm", u"\u65b0\u589e", None))
        self.btn_virus_refresh.setText(QCoreApplication.translate("MainForm", u"\u5237\u65b0\u540d\u79f0", None))
        self.groupBox_8.setTitle(QCoreApplication.translate("MainForm", u"\u7f13\u5b58", None))
        self.label_11.setText(QCoreApplication.translate("MainForm", u"\u65e0\u6cd5\u8bc6\u522b\u5230Wallpaper\u66f4\u65b0\u64cd\u4f5c\u3002\n"
"\u7f3a\u5931\u90e8\u5206\u58c1\u7eb8\u53ef\u4ee5\u5173\u95edWallpaper\u540e\u7b49\u5f85\u4e00\u6bb5\u65f6\u95f4\u65b0\u6570\u636e\u751f\u6210\uff0c\u518d\u5c1d\u8bd5\u6b64\u64cd\u4f5c\u3002", None))
        self.btn_restart.setText(QCoreApplication.translate("MainForm", u"\u5f3a\u5236\u5237\u65b0(\u672a\u5b8c\u5584)", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainForm", u"\u89e3\u9501\u9690\u85cf\u6210\u5c31\u300c30\u6761\u547d\u300d", None))
        self.label_9.setText(QCoreApplication.translate("MainForm", u"\u6253\u5f00\u58c1\u7eb8\u8bbe\u7f6e\uff0c\u5207\u6362\u5230\u5173\u4e8e\u9875\u9762\uff0c\u70b9\u51fb\u89e3\u9501\n"
"\n"
"\u6216\u8005\u624b\u52a8\u8f93\u5165\u201d\u4e0a\u4e0a\u4e0b\u4e0b\u5de6\u53f3\u5de6\u53f3ba\u56de\u8f66\u201c", None))
        self.btn_unlock_hidden_achievements.setText(QCoreApplication.translate("MainForm", u"\u89e3\u9501", None))
        self.groupBox_info.setTitle(QCoreApplication.translate("MainForm", u"\u5173\u4e8e", None))
        self.label_version.setText(QCoreApplication.translate("MainForm", u"\u7248\u672c\uff1a0", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_set), QCoreApplication.translate("MainForm", u"\u8bbe\u7f6e", None))
    # retranslateUi

