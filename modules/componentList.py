
from PySide6.QtWidgets import QApplication, QWidget
from widgets import Ui_ListWidget
from .componentListItem import MyWindow as Ui_ListItem

class MyWindow(QWidget, Ui_ListWidget):
    def __init__(self, type):
        self.type = type
        super().__init__()
        self.setupUi(self)
        if type == 'main':
            pass
            # self.set_list(data)
        elif type == 'backup':
            self.checkBox_invalid.setVisible(False)
            self.btn_invalid.setVisible(False)

    # 设置列表数据
    def setData(self, data):
        self.tableWidget_main.horizontalHeader().setStretchLastSection(True) # 表格自适应
        self.tableWidget_main.horizontalHeader().setVisible(False) # 隐藏头
        self.tableWidget_main.verticalHeader().setVisible(False) # 隐藏侧边
        self.tableWidget_main.setColumnCount(1)
        self.tableWidget_main.setRowCount(len(data))
        for index, item in enumerate(data):
            self.tableWidget_main.setRowHeight(index, 140)
            boxItem = Ui_ListItem()
            boxItem.setData(item['name'], item['path'])
            self.tableWidget_main.setCellWidget(index, 0, boxItem)

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()