import os
import json
import logging

from PySide6.QtCore import QMetaObject, QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget, QSpacerItem, QSizePolicy

class Ui_tableItemBox(QWidget):
    def __init__(self):
        super().__init__()  # 必须调用父类初始化
        self.setupUi()
        
    def setupUi(self):
        if not self.objectName():
            self.setObjectName(u"tableItemBox")
        self.resize(140, 140)
        self.setMinimumSize(QSize(0, 140))
        self.setMaximumSize(QSize(16777215, 140))
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_img = QLabel(self)
        self.label_img.setObjectName(u"label_img")
        self.label_img.setMinimumSize(QSize(120, 120))
        self.label_img.setMaximumSize(QSize(120, 120))
        self.label_img.setScaledContents(True)
        self.label_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.horizontalLayout.addWidget(self.label_img)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_name = QLabel(self)
        self.label_name.setObjectName(u"label_name")
        self.horizontalLayout_2.addWidget(self.label_name)
        self.btn_RePKG = QPushButton(self)
        self.btn_RePKG.setVisible(False)
        self.btn_RePKG.setObjectName(u"btn_RePKG")
        self.btn_RePKG.setMaximumSize(QSize(80, 16777215))
        self.horizontalLayout_2.addWidget(self.btn_RePKG)
        self.btn_open = QPushButton(self)
        self.btn_open.setObjectName(u"btn_open")
        self.btn_open.setMaximumSize(QSize(80, 16777215))
        self.horizontalLayout_2.addWidget(self.btn_open)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.label_title = QLabel(self)
        self.label_title.setObjectName(u"label_title")
        self.verticalLayout_2.addWidget(self.label_title)
        self.label_note = QLabel(self)
        self.label_note.setObjectName(u"label_note")
        self.verticalLayout_2.addWidget(self.label_note)
        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(self.verticalSpacer)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        # self.retranslateUi()
        QMetaObject.connectSlotsByName(self)
    # setupUi


    def retranslateUi(self, name, path):
        self.btn_open.setText('打开')
        self.btn_open.clicked.connect(lambda: os.startfile(path))
        self.btn_RePKG.setText('提取')

        try:
            projectPath = os.path.join(path, 'project.json')
            with open(projectPath, encoding="utf-8") as f1:
                obj = json.load(f1) # 从文件读取json并反序列化
                imgPath = os.path.join(path, obj['preview'])
                isImgPath = os.path.isfile(imgPath)
                # self.label_img.setText("")
                self.label_img.setPixmap(QPixmap(imgPath if isImgPath else './img/Management.ico'))
                if 'type' in obj:
                    name = name + ':' + obj['type']
                    if obj['type'].lower() == 'scene':
                        self.btn_RePKG.setVisible(True)
                elif 'dependency' in obj:
                    name = name + ':' + obj['dependency']
                self.label_name.setText(name)
                self.label_title.setText(obj['title'])
                if 'description' in obj: self.label_note.setText(obj['description'])
        except Exception as e:
            logging.warning(f"Warning accessing registry: {name, e}")
    # retranslateUi