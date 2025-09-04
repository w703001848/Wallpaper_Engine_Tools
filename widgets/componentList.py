
from PySide6.QtWidgets import QApplication, QWidget
from .Ui_list import Ui_ListWidget
from .componentListItem import MyWindow as Ui_Item
from modules.Config import get_workshopcache_page, temp_workshopcache_size
from modules.main import timer, dirSizeToStr

class MyWindow(QWidget, Ui_ListWidget):
    def __init__(self, type):
        self.type = type

        super().__init__()
        self.setupUi(self)
        
        self.initPage()

        if type == 'main':
            self.label_capacity.setText(f"容量：{dirSizeToStr(temp_workshopcache_size)}")
            self.setData()
        elif type == 'backup':
            self.checkBox_invalid.setVisible(False)
            self.btn_invalid.setVisible(False)
    
    def initPage(self):
        self.tableWidget_main.horizontalHeader().setStretchLastSection(True) # 表格自适应
        self.tableWidget_main.horizontalHeader().setVisible(False) # 隐藏头
        self.tableWidget_main.verticalHeader().setVisible(False) # 隐藏侧边
        self.tableWidget_main.setColumnCount(1)

    # 设置列表数据
    def setData(self):
        with timer("加载列表耗时"):
            data = get_workshopcache_page(0, 20)
            self.tableWidget_main.setRowCount(len(data))
            for index, item in enumerate(data):
                self.tableWidget_main.setRowHeight(index, 140)
                boxItem = Ui_Item(self.type)
                boxItem.setData(item)
                self.tableWidget_main.setCellWidget(index, 0, boxItem)

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()