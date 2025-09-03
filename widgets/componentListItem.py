import os, json, logging

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget
from .Ui_listItem import Ui_ItemFrame

from modules.RePKG import processItem

class MyWindow(QWidget, Ui_ItemFrame):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btn_RePKG.setVisible(False)


    # 设置数据
    def setData(self, name, path):
        self.btn_open.clicked.connect(lambda: os.startfile(path))

        try:
            projectPath = os.path.join(path, 'project.json')
            with open(projectPath, encoding="utf-8") as f1:
                obj = json.load(f1) # 从文件读取json并反序列化
                imgPath = os.path.join(path, obj['preview'])
                isImgPath = os.path.isfile(imgPath)
                self.label_img.setPixmap(QPixmap(imgPath if isImgPath else './img/Management.ico'))
                self.label_title.setText(obj['title'])
                if 'description' in obj:
                    self.label_note.setText(obj['description'])
                if 'type' in obj:
                    name = f"{name}【{obj['type']}】"
                    if obj['type'].lower() == 'scene':
                        self.btn_RePKG.setVisible(True)
                        self.btn_RePKG.clicked.connect(lambda: processItem(os.path.join(path, 'scene.pkg'), True))
                elif 'dependency' in obj:
                    name = f"{name}【{obj['dependency']}】"
                self.label_name.setText(name)
        except Exception as e:
            logging.warning(f"设置数据: {name, e}")

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()