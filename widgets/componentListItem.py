import os, json, logging

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget
from .Ui_listItem import Ui_ItemFrame

from modules.RePKG import processItem

class MyWindow(QWidget, Ui_ItemFrame):
    def __init__(self, type):
        super().__init__()
        self.setupUi(self)
        self.btn_RePKG.setVisible(False)
        if type == 'main':
            self.btn_name_edit.setVisible(False)
            self.btn_title_edit.setVisible(False)

    # 设置数据
    def setData(self, data):
        self.label_name.setText(f"{data['workshopid']}【{self.get_type_str(data['type'])}】")
        self.label_title.setText(data['title'])
        imgPath = data["preview"]
        isImgPath = os.path.isfile(imgPath)
        self.label_img.setPixmap(QPixmap(imgPath if isImgPath else './img/Management.ico'))
        # if 'type' in data:
        if data['type'].lower() == 'scene':
            self.btn_RePKG.setVisible(True)
            self.btn_RePKG.clicked.connect(lambda: processItem(data["file"], True))
        self.btn_open.clicked.connect(lambda: os.startfile(os.path.dirname(data["preview"])))
        # if 'description' in data:
        #     try:
        #         with open(data["project"], encoding="utf-8") as f1:
        #             obj = json.load(f1) # 从文件读取json并反序列化
        #             if 'description' in obj:
        #                 data["dependency"] = obj["dependency"]
        #                 self.label_note.setText(obj['description'])
        #             else:
        #                 data["dependency"] = ""
        #     except Exception as e:
        #         logging.warning(f"设置数据: e")

    def get_type_str(self, key):
        typeStr = "未知"
        if key.lower() == "scene":
            typeStr = "场景"
        elif key.lower() == "video":
            typeStr = "视频"
        elif key.lower() == "web":
            typeStr = "网页"
        elif key.lower() == "application":
            typeStr = "应用"
        return typeStr

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()