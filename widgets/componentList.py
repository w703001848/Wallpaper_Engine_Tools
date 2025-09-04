import math

from PySide6.QtCore import QStringListModel
from PySide6.QtWidgets import QApplication, QWidget

from .Ui_list import Ui_ListWidget

from .componentListItem import MyWindow as Ui_Item

from modules.Config import temp_workshopcache, config, set_config
from modules.main import timer, dirSizeToStr

class MyWindow(QWidget, Ui_ListWidget):

    def __init__(self, keyType):
        self.keyType = keyType
        self.data = [] # 列表数据
        self.page = 1 # 当前页
        self.total_page = 1 # 总页数
        self.total_size = 0 # 总数量
        self.filter_total_size = 0 # 筛选后总数量
        self.filterSize = [10, 20, 30, 50]
        self.sortCurrent = ['title', 'favorite', 'filesize', 'subscriptiondate', 'updatedate']
        self.sort = {
            "isCheckedScene": config["isCheckedScene"],
            "isCheckedVideo": config["isCheckedVideo"],
            "isCheckedWeb": config["isCheckedWeb"],
            "isCheckedApplication": config["isCheckedApplication"],
            "isCheckedInvalid": config["isCheckedInvalid"],
            "filterSize": config["filterSize"],
            "sortCurrent": config["sortCurrent"], # 订阅日期: subscriptiondate
        }
        super().__init__()
        
        with timer("初始化耗时"):
            self.initPage()
            self.update(True)

    
    def initPage(self):
        self.setupUi(self)
        self.checkBox_scene.keyType = "isCheckedScene"
        self.checkBox_video.keyType = "isCheckedVideo"
        self.checkBox_web.keyType = "isCheckedWeb"
        self.checkBox_application.keyType = "isCheckedApplication"
        self.checkBox_invalid.keyType = "isCheckedInvalid"
        self.checkBox_scene.setChecked(self.sort["isCheckedScene"])
        self.checkBox_video.setChecked(self.sort["isCheckedVideo"])
        self.checkBox_web.setChecked(self.sort["isCheckedWeb"])
        self.checkBox_application.setChecked(self.sort["isCheckedApplication"])
        self.checkBox_invalid.setChecked(self.sort["isCheckedInvalid"])
        self.comboBox_sort.currentIndexChanged.connect(self.handleSortSelect)
        self.comboBox_size.currentIndexChanged.connect(self.handleSizeSelect)
        self.comboBox_page.currentIndexChanged.connect(self.handlePageSelect)
        self.btn_left.keyType = "sub"
        self.btn_left.setVisible(False)
        self.btn_right.keyType = "add"
        self.buttonGroup_page.buttonClicked.connect(self.handlePageBtn)
        self.buttonGroup_filter.buttonClicked.connect(self.handleFilterGroup)
        self.tableWidget_main.horizontalHeader().setStretchLastSection(True) # 表格自适应
        self.tableWidget_main.horizontalHeader().setVisible(False) # 隐藏头
        self.tableWidget_main.verticalHeader().setVisible(False) # 隐藏侧边
        self.tableWidget_main.setColumnCount(1)

    # 计算总数量和总容量（计算一次）
    def getSizeAndCapacity(self):
        total_capacity = 0
        for obj in self.data:
            total_capacity += obj["filesize"]
        print(f"总容量：{total_capacity}")
        self.label_capacity.setText(f"容量：{dirSizeToStr(total_capacity)}")
        self.total_size = len(self.data)
        print(f"工坊壁纸缓存合未知项目总数量：{self.total_size}")

    def update(self, isFirst = False):
        print('update')
        self.page = 1
        if self.keyType == 'main':
            self.data = temp_workshopcache
        elif self.keyType == 'backup':
            # data = temp_workshopcache
            if isFirst:
                self.checkBox_invalid.setVisible(False)
                self.btn_invalid.setVisible(False)
        if isFirst:
            self.getSizeAndCapacity()
        # 筛选
        def filterData(item):
            keyType = item["type"].lower()
            if not self.sort["isCheckedInvalid"] and (item["authorsteamid"] == ""):
                return False
            elif self.sort["isCheckedScene"] and keyType == "scene":
                return True
            elif self.sort["isCheckedVideo"] and keyType == "video":
                return True
            elif self.sort["isCheckedWeb"] and keyType == "web":
                return True
            elif self.sort["isCheckedApplication"] and keyType == "application":
                return True
            else:
                if self.sort["isCheckedInvalid"] and (item["authorsteamid"] == ""):
                    return True
                else:
                    return False

        # print(f"筛选前长度：{len(self.data)}")
        self.data = list(filter(filterData, self.data))
        self.filter_total_size = len(self.data) # 筛选后长度
        self.label_filter.setText(f"筛选结果（ {self.total_size} 个中有 {self.filter_total_size} 个）")
        self.setPage()

    # 更新总页数
    def setPage(self):
        print(f'setPage {self.filter_total_size}')
        self.total_page = math.ceil(self.filter_total_size / self.sort["filterSize"])
        self.label_page.setText(f"共 {self.total_page} 页")
        model = QStringListModel()
        pageData = []
        for i in range(0, self.total_page):
            pageData.append(str(i+1))
        model.setStringList(pageData)
        self.comboBox_page.setModel(model)
        self.setBtnPage(self.page)

    # 设置列表数据
    def setData(self):
        print(f'setData {len(self.data)}')
        # 排序(除了名称倒序，其他都是正序)
        self.data.sort(key=lambda x:x[self.sort["sortCurrent"]], reverse = self.sort["sortCurrent"] != 'title')

        self.tableWidget_main.setRowCount(0)
        if self.total_page == self.page:
            self.tableWidget_main.setRowCount(self.filter_total_size % self.sort["filterSize"])
        else:
            if self.filter_total_size < self.sort["filterSize"]:
                self.tableWidget_main.setRowCount(self.filter_total_size)
            else:
                self.tableWidget_main.setRowCount(self.sort["filterSize"])
        # 截取
        start = (self.page - 1) * self.sort["filterSize"]
        end = self.page * self.sort["filterSize"]
        if end > self.filter_total_size:
            end = None
        for index, item in enumerate(self.data[start:end]): # 截取功能要浅拷贝处理，否则会加载上次截取
            self.tableWidget_main.setRowHeight(index, 140)
            boxItem = Ui_Item(self.keyType)
            boxItem.setData(item)
            self.tableWidget_main.setCellWidget(index, 0, boxItem)

    # 筛选组
    def handleFilterGroup(self, event):
        print(f"筛选组 {event.keyType} {event.isChecked()}")
        self.sort[event.keyType] = event.isChecked()
        set_config(event.keyType, event.isChecked())

        with timer("加载列表耗时"):
            self.update()
    
    # 数量选择
    def handleSizeSelect(self, index):
        self.sort["filterSize"] = self.filterSize[index]
        set_config("filterSize", self.sort["filterSize"])
        print(f'数量选择 index:{index} filterSize:{self.sort["filterSize"]}')
        self.setPage()

    # 排序选择
    def handleSortSelect(self, index):
        self.sort["sortCurrent"] = self.sortCurrent[index]
        set_config("sortCurrent", self.sort["sortCurrent"])
        print(f'排序选择 index:{index} sortCurrent:{self.sort["sortCurrent"]}')
        self.setData()
    
    # 页选择
    def handlePageSelect(self, index):
        self.page = index + 1
        print(f"页选择 index:{index} page:{self.page}")
        self.setData()

    # 页切换按钮
    def handlePageBtn(self, event):
        print(f"页切换按钮 {event.keyType} {self.page} {type(self.page)}")
        num = self.page
        if event.keyType == 'add':
            num += 1
        elif event.keyType == 'sub':
            num -= 1
        
        self.comboBox_page.setCurrentIndex(num - 1) # 执行位置不对 self.page 容易被其他代码污染
        self.setBtnPage(num)

    def setBtnPage(self, num):
        if num == self.total_page:
            print(f"setBtnPage right on num:{num} total_page:{self.total_page}")
            self.btn_right.setVisible(False)
        else:
            print(f"setBtnPage right ok num:{num} total_page:{self.total_page}")
            self.btn_right.setVisible(True)
        if num <= 1:
            print(f"setBtnPage left no num:{num} total_page:{self.total_page}")
            self.btn_left.setVisible(False)
            self.comboBox_page.setVisible(num != 0)
        else:
            print(f"setBtnPage left ok num:{num} total_page:{self.total_page}")
            self.btn_left.setVisible(True)
        self.page = num

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()