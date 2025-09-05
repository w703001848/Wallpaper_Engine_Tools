import os, atexit, pyperclip
import sys, subprocess
import logging, json, math
# PySide6组件调用
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QWidget, QLabel
# 加载模板
from widgets.Ui_main import Ui_MainForm
# 功能模块
from modules.main import Debouncer, timer, Unlock_hidden_achievements, dirSizeToStr, openFileDialog, openDirDialog, openMessageDialog, openStartfile
from modules.Config import config, temp_workshop, temp_authorblocklistnames, setSteamPath, setWallpaperPath, setWallpaperBackupPath, setConfig, saveConfig
from modules.RePKG import runRepkg, followWork, updateRepkgData
from modules.Mklink import mklinkCreate, mklinkNew, mklinkBack, updateMklinkList

class MyWindow(QWidget, Ui_MainForm):
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        with timer("初始化耗时"):
            self.initPage()
            self.initMain()
            self.initRepkg()
            self.initMklink()
            # self.initNaslink()
            self.initAuthorblock()

            # 加载数据
            # self.tabChange()
            self.loadData(True)
            
        # 监听退出保存config
        atexit.register(saveConfig)

    def func(self, *args, **kwargs):
        print(11112)
        pass

    # 初始化界面
    def initPage(self):
        # tab页切换
        self.tabWidget.currentChanged.connect(self.tabChange)

        # 获取steam地址
        steam_path = config["steamPath"]
        self.lineEdit_steamPath.setText(steam_path)

        # 设置文本框steam地址
        def handleSteamPathClick():
            __path = openFileDialog(config["steamPath"], "请选择steam.exe启动文件", "Steam (*.exe)")
            if __path:
                setSteamPath(__path)
                self.lineEdit_steamPath.setText(__path)
        self.btn_steamPath.clicked.connect(handleSteamPathClick)

        # 获取wallpaper地址
        if config["wallpaperPath"]:
            
            # 设置文本框wallpaper地址
            def handleWallpaperPathClick():
                __path = openFileDialog(config["wallpaperPath"], "请选择wallpaper_engine/launcher.exe启动文件", "Steam (*.exe)")
                if __path:
                    setWallpaperPath(__path)
                    self.lineEdit_wallpaperPath.setText(__path)
            self.btn_wallpaperPath.clicked.connect(handleWallpaperPathClick)
            self.lineEdit_wallpaperPath.setText(config["wallpaperPath"])
            
            # 设置文本框backup地址
            def handleBackupPathClick():
                __path = openDirDialog(config["backupPath"])
                if __path:
                    setWallpaperBackupPath(__path)
                    self.lineEdit_wallpaperBackupPath.setText(__path)
            self.btn_wallpaperBackupPath.clicked.connect(handleBackupPathClick)
            self.lineEdit_wallpaperBackupPath.setText(config["backupPath"])

        self.label_version.setText('版本：' + config["version"])
        self.btn_unlock_hidden_achievements.clicked.connect(Unlock_hidden_achievements) # 解锁成就
        self.checkBox_dir.clicked.connect(lambda event: setConfig("isFolders", not event)) # 分类文件夹锁定

        # 调用此函数以重启应用
        def showRestartConfirmation():
            if openMessageDialog("清空缓存数据并重启，请确认！"):
                setConfig("isCheckedScene", True) # 场景
                setConfig("isCheckedVideo", True) # 视频
                setConfig("isCheckedWeb", True) # 网页
                setConfig("isCheckedApplication", True) # 应用
                setConfig("isCheckedInvalid", True) # 失效
                setConfig("filterSize", 30) # 分页
                setConfig("sortCurrent", "subscriptiondate") # 订阅日期
                # 获取当前脚本的路径
                script_path = sys.argv[0]
                # 获取当前脚本的目录，以防脚本不在工作目录中
                script_dir = os.path.dirname(os.path.realpath(script_path))
                # 使用subprocess启动新进程，传递所有命令行参数
                subprocess.Popen([sys.executable, script_path] + sys.argv[1:])
                # 退出当前进程
                sys.exit(0)
        self.btn_restart.clicked.connect(showRestartConfirmation) # 清空缓存重启

    # 初始化壁纸
    def initMain(self):
        self.data = [] # 列表数据
        self.page = 1 # 当前页
        self.total_page = 1 # 总页数
        self.total_size = 0 # 总数量
        self.filter_total_size = 0 # 筛选后总数量
        self.filterSize = [10, 20, 30, 50]
        self.sortCurrent = ["title", "ratingrounded", "favorite", "filesize", "subscriptiondate", "updatedate"]
        self.sort = {
            "isCheckedScene": config["isCheckedScene"],
            "isCheckedVideo": config["isCheckedVideo"],
            "isCheckedWeb": config["isCheckedWeb"],
            "isCheckedApplication": config["isCheckedApplication"],
            "isCheckedWallpaper": config["isCheckedWallpaper"],
            "isCheckedBackup": config["isCheckedBackup"],
            "isCheckedInvalid": config["isCheckedInvalid"],
            "isCheckedAuthorblock": config["isCheckedAuthorblock"],
            "sortCurrent": config["sortCurrent"], # 订阅日期: subscriptiondate
            "sortReverse": config["sortReverse"], # 排序 正序
            "filterSize": config["filterSize"],
            "displaySize": config["displaySize"], # 显示大小
        }

        if not config['mklinkList'][0]["path"]:
            self.tableWidget_main.setVisible(False)
            return

        self.label_error.setVisible(False)
        self.tableWidget_main.horizontalHeader().setStretchLastSection(True) # 表格自适应
        # self.tableWidget_main.horizontalHeader().setVisible(False) # 隐藏头
        # self.tableWidget_main.verticalHeader().setVisible(False) # 隐藏侧边
        self.tableWidget_main.setColumnCount(1)

        def handleDirNewClick():
            print("新增按钮")
        self.btn_dir_new.clicked.connect(handleDirNewClick)

        def handleInvalidClick():
            print("删除失效按钮")
        self.btn_invalid.clicked.connect(handleInvalidClick)
        
        def handleSearchClick():
            txt = self.lineEdit_search.text()
            print(f"查询文本: {txt}")
            self.btn_clear.setVisible(True)
        self.btn_search.clicked.connect(handleSearchClick)
        
        def handleSearchClearClick():
            self.lineEdit_search.setText("")
            print("清空查询文本")
            self.btn_clear.setVisible(False)
        self.btn_clear.clicked.connect(handleSearchClearClick)
        self.btn_clear.setVisible(False)

        # 筛选组 类型
        def handleGroupFilter(event):
            print(f"筛选组 类型 {event.keyType} {event.isChecked()}")
            self.sort[event.keyType] = event.isChecked()
            setConfig(event.keyType, event.isChecked())
            # with timer("加载列表耗时"):
            #     self.loadData()
        self.buttonGroup_type.buttonClicked.connect(handleGroupFilter) # 类型
        self.checkBox_scene.keyType = "isCheckedScene"
        self.checkBox_video.keyType = "isCheckedVideo"
        self.checkBox_web.keyType = "isCheckedWeb"
        self.checkBox_application.keyType = "isCheckedApplication"
        self.checkBox_scene.setChecked(self.sort["isCheckedScene"])
        self.checkBox_video.setChecked(self.sort["isCheckedVideo"])
        self.checkBox_web.setChecked(self.sort["isCheckedWeb"])
        self.checkBox_application.setChecked(self.sort["isCheckedApplication"])

        # 筛选组 来源
        def handleGroupFilter2(event):
            print(f"筛选组 来源 {event.keyType} {event.isChecked()}")
            self.sort[event.keyType] = event.isChecked()
            setConfig(event.keyType, event.isChecked())
        self.buttonGroup_source.buttonClicked.connect(handleGroupFilter2) # 来源
        self.checkBox_wallpaper.keyType = "isCheckedWallpaper"
        self.checkBox_backup.keyType = "isCheckedBackup"
        self.checkBox_invalid.keyType = "isCheckedInvalid"
        self.checkBox_wallpaper.setChecked(self.sort["isCheckedWallpaper"])
        self.checkBox_backup.setChecked(self.sort["isCheckedBackup"])
        self.checkBox_invalid.setChecked(self.sort["isCheckedInvalid"])

        # 黑名单关联
        def handleAuthorblockClick(isChecked):
            print(f"黑名单关联 {isChecked}")
            self.sort["isCheckedAuthorblock"] = isChecked
            setConfig("isCheckedAuthorblock", isChecked)
        self.checkBox_authorblock.clicked.connect(handleAuthorblockClick)
        self.checkBox_authorblock.keyType = "isCheckedAuthorblock"
        self.checkBox_authorblock.setChecked(self.sort["isCheckedAuthorblock"])

        # 排序选择
        def handleSortSelect(index):
            self.sort["sortCurrent"] = self.sortCurrent[index]
            setConfig("sortCurrent", self.sort["sortCurrent"])
            print(f'排序选择 index:{index} sortCurrent:{self.sort["sortCurrent"]}')
            # self.refreshData()
        self.comboBox_sort.currentIndexChanged.connect(handleSortSelect)

        # 排序
        def handleGroupSort(event):
            print(f"排序 keyType:{event.keyType}")
            self.sort["sortReverse"] = event.keyType == 'reverse'
            setConfig("sortReverse", self.sort["sortReverse"])
            # self.refreshData()
        self.buttonGroup_sort.buttonClicked.connect(handleGroupSort) # 排序
        self.radioButton_positive.keyType = 'positive'
        self.radioButton_reverse.keyType = 'reverse'

        # 查看大小
        def handleGroupImg(event):
            print(f"查看大小 keyType:{event.keyType}")
            self.sort["displaySize"] = event.keyType
            setConfig("displaySize", self.sort["displaySize"])
            # self.refreshData()
        self.buttonGroup_img.buttonClicked.connect(handleGroupImg) # 查看大小
        self.radioButton_big.keyType = 'big'
        self.radioButton_small.keyType = 'small'

        # 数量选择
        def handleSizeSelect(index):
            self.sort["filterSize"] = self.filterSize[index]
            setConfig("filterSize", self.sort["filterSize"])
            print(f'数量选择 index:{index} filterSize:{self.sort["filterSize"]}')
            # self.refreshData()
        self.comboBox_size.currentIndexChanged.connect(handleSizeSelect)

        # 页选择
        def handlePageSelect(index):
            self.page = index + 1
            print(f"页选择 index:{index} page:{self.page}")
            self.redrawBtn(self.page)
            self.loadData() # 数据刷新入口都在这
        self.comboBox_page.currentIndexChanged.connect(handlePageSelect)
        # 页切换按钮
        def handleGroupPage(event):
            print(f"页切换按钮 {event.keyType} {self.page} {type(self.page)}")
            num = self.page
            if event.keyType == 'add':
                num += 1
            elif event.keyType == 'sub':
                num -= 1
            self.comboBox_page.setCurrentIndex(num - 1) # 关联页选择
        self.buttonGroup_page.buttonClicked.connect(handleGroupPage) # 页左右切
        self.btn_left.keyType = "sub"
        self.btn_right.keyType = "add"
        self.btn_left.setVisible(False)

    # 加载数据
    def loadData(self, isFirst = False):
        print('loadData')
        self.page = 1
        self.data = temp_workshop
        if isFirst:
            # 计算总数量和总容量（计算一次）
            total_capacity = 0
            for obj in self.data:
                total_capacity += obj["filesize"]
            print(f"总容量：{total_capacity}")
            self.label_capacity.setText(f"容量：{dirSizeToStr(total_capacity)}")
            self.total_size = len(self.data)
            print(f"工坊壁纸缓存合未知项目总数量：{self.total_size}")
        
        # 筛选来源
        def filterData(obj):
            keySource = obj["source"].lower()
            
            # 筛选类型
            def filterType():
                nonlocal obj
                keyType = obj["type"].lower()
                if self.sort["isCheckedScene"] and keyType == "scene":
                    return True
                elif self.sort["isCheckedVideo"] and keyType == "video":
                    return True
                elif self.sort["isCheckedWeb"] and keyType == "web":
                    return True
                elif self.sort["isCheckedApplication"] and keyType == "application":
                    return True
                return False
            
            if self.sort["isCheckedWallpaper"] and keySource == "wallpaper":
                return filterType()
            elif self.sort["isCheckedBackup"] and keySource == "backup":
                return filterType()
            elif self.sort["isCheckedInvalid"] and keySource == "invalid":
                return filterType()
            return False
        print(f"筛选前长度：{len(self.data)}")
        self.data = list(filter(filterData, self.data))
        self.filter_total_size = len(self.data) # 筛选后长度
        self.label_filter.setText(f"筛选结果（ {self.total_size} 个中有 {self.filter_total_size} 个）")

        # 重新计算总页数
        print(f'重新计算总页数calculateQuantity {self.filter_total_size}')
        self.total_page = math.ceil(self.filter_total_size / self.sort["filterSize"])
        self.label_page.setText(f"共 {self.total_page} 页")
        model = QStringListModel()
        pageData = []
        for i in range(0, self.total_page):
            pageData.append(str(i+1))
        model.setStringList(pageData)
        self.comboBox_page.setModel(model) # ？会触发刷新数据
        self.redrawBtn(self.page)

    # 设置列表数据
    def refreshData(self):
        print(f'refreshData {len(self.data)}')
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

    # 重绘翻页按钮
    def redrawBtn(self, num):
        if num >= self.total_page:
            print(f"redrawBtn right on num:{num} total_page:{self.total_page}")
            self.btn_right.setVisible(False)
        else:
            print(f"redrawBtn right ok num:{num} total_page:{self.total_page}")
            self.btn_right.setVisible(True)
        if num <= 1:
            print(f"redrawBtn left no num:{num} total_page:{self.total_page}")
            self.btn_left.setVisible(False)
            self.comboBox_page.setVisible(self.total_page != 0)
        else:
            print(f"redrawBtn left ok num:{num} total_page:{self.total_page}")
            self.btn_left.setVisible(True)
        self.page = num

    # repkg初始化
    def initRepkg(self):
        self.tableWidget_repkg.horizontalHeader().setStretchLastSection(True) # 表格自适应
        # self.tableWidget_repkg.horizontalHeader().setVisible(True) # 隐藏头
        # self.tableWidget_repkg.verticalHeader().setVisible(True) # 隐藏侧边
        self.debouncer = Debouncer(lambda: updateRepkgData(self.tableWidget_repkg, self.size().width(), False), 700)

        # repkg选择
        def handleRepkgPathClick():
            __path = openFileDialog(config["repkgPath"], "请在场景壁纸中选择一个PKG/MPKG文件", "PKG/MPKG Files (*.pkg;*.mpkg)")
            if __path:
                self.lineEdit_repkg.setText(__path)
        self.btn_repkgPath.clicked.connect(handleRepkgPathClick)

        # repkg提取
        def handleRepkgExtractClick():
            __path = self.lineEdit_repkg.text()
            if runRepkg(__path):
                if followWork():
                    # 打开资源管理器
                    # os.startfile(os.path.join(os.getcwd(), "output"))
                    updateRepkgData(self.tableWidget_repkg)
                    setConfig('repkgPath', __path)
        self.btn_repkg.clicked.connect(handleRepkgExtractClick)

    # 软地址初始化
    def initMklink(self):
        self.btn_mklink_open_old.clicked.connect(lambda: openStartfile(self.lineEdit_mklink_path.text())) # mklink打开资源管理器
        self.btn_mklink_open.clicked.connect(lambda: openStartfile(self.lineEdit_mklink_path_new.text())) # mklink打开资源管理器

        # 软地址切换
        def handleMklinkChange(event):
            index = self.listWidget_mklink.currentRow()
            obj = config["mklinkList"][index]
            self.lineEdit_mklink_path.setText(obj['path'])
            self.lineEdit_mklink_path_new.setText(obj['path_new'])
            self.btn_mklink_remove.setVisible(index > 1) # 第三个开始判定
        self.listWidget_mklink.currentItemChanged.connect(handleMklinkChange) # 表格点击

        # 新增
        def handleMklinkNewClick():
            obj = mklinkNew()
            if obj:
                self.listWidget_mklink.addItem(f"标注:{obj['name']}\n{obj['path']}\n未生成")
        self.btn_mklink_new.clicked.connect(handleMklinkNewClick)

        # 移除
        def handleMklinkRemoveClick():
            index = self.listWidget_mklink.currentRow()
            del config["mklinkList"][index]
            self.listWidget_mklink.takeItem(index)
            self.listWidget_mklink.setCurrentRow(1) # 选中
        self.btn_mklink_remove.clicked.connect(handleMklinkRemoveClick)

        # 生成软链接
        def handleMklinkCreateClick():
            index = self.listWidget_mklink.currentRow()
            dir_path_new = mklinkCreate(index)
            if dir_path_new:
                obj = config["mklinkList"][index]
                obj['path_new'] = dir_path_new
                self.listWidget_mklink.currentItem().setText(f"标注:{obj['name']}\n{obj['path']}\n{obj['path_new'] or '未生成'}")
                self.lineEdit_mklink_path_new.setText(obj['path_new'])
        self.btn_mklink_create.clicked.connect(handleMklinkCreateClick)

        # 还原
        def handleMklinkBackClick():
            index = self.listWidget_mklink.currentRow()
            if mklinkBack(index):
                obj = config["mklinkList"][index]
                obj['path_new'] = ""
                self.listWidget_mklink.currentItem().setText(f"标注:{obj['name']}\n{obj['path']}\n未生成")
                self.lineEdit_mklink_path_new.setText("")
        self.btn_mklink_restore.clicked.connect(handleMklinkBackClick)

    # 软地址初始化
    def initAuthorblock(self):
        # 黑名单列表点击
        def handleAuthorblockClick():
            obj = temp_authorblocklistnames[self.listWidget_authorblock.currentRow()]
            openMessageDialog("已复制到剪贴板")
            pyperclip.copy(f"名称: {obj['name']}{os.linesep}ID: {obj['value']}")
        self.listWidget_authorblock.itemClicked.connect(handleAuthorblockClick)

    # 黑名单列表数据加载
    def get_addauthorblock_list(self):
        if len(temp_authorblocklistnames) != self.listWidget_authorblock.count():
            print('黑名单列表加载数据')
            for item in temp_authorblocklistnames:
                self.listWidget_authorblock.addItem(f"名称: {item['name']}{os.linesep}ID: {item['value']}")

    # 窗口变化
    def resizeEvent(self, event):
        # print(f"窗口大小已更新为: {self.size().width()}x{self.size().height()}")
        if self.tabWidget.currentIndex() == 1:
            self.debouncer.trigger()

    # tabWidget切换
    def tabChange(self):
        index = self.tabWidget.currentIndex()
        if index == 1: # repkg加载
            # repkg列表更新
            path = config["repkgPath"]
            print(f"repkg加载{os.linesep}提取地址:{self.lineEdit_repkg.text()}{os.linesep}上次提取:{path}")
            if path != '' and self.lineEdit_repkg.text() != path: # 防止重复刷新
                # Repkg刷新
                self.lineEdit_repkg.setText(path)
                updateRepkgData(self.tableWidget_repkg)
        elif index == 2: # Mklink加载
            updateMklinkList(self.listWidget_mklink)
        elif index == 3: # NAS备份加载
            pass
        elif index == 4: # 黑名单加载
            self.get_addauthorblock_list()


if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()
