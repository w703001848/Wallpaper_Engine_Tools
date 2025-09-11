import os, sys, subprocess, atexit, pyperclip
import logging, math, time, json
# PySide6组件调用
from PySide6.QtCore import Qt, QSize, QStringListModel
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QListWidgetItem
# 加载模板
from widgets.Ui_main import Ui_MainForm
# 功能模块
from modules.main import Debouncer, timer, Unlock_hidden_achievements, getDirSize, dirSizeToStr, openFileDialog, openDirDialog, openMessageDialog, openStartfile
from modules.Config import config, temp_authorblocklistnames, getWorkshop, setSteamPath, setWallpaperPath, setWallpaperBackupPath, setConfig, saveConfig
from modules.RePKG import runRepkg, followWork, updateRepkgData
from modules.Mklink import mklinkCreate, mklinkNew, mklinkBack, updateMklinkList
# 资源图片
from img import images_rc

class MyWindow(QWidget, Ui_MainForm):
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 监听退出保存config
        atexit.register(saveConfig)

        with timer("初始化耗时"):
            self.initPage()
            self.initMain()
            self.initMainRight()
            self.initRepkg()
            self.initMklink()
            # self.initNaslink()
            self.initAuthorblock()

            # 加载数据
            self.loadData(True)

    # 初始化界面
    def initPage(self):
        # 窗口大小变化防抖
        self.windowWidth = self.size().width() # 记录窗口大小
        def resizeWindow():
            print(f"窗口大小已更新为: {self.size().width()}x{self.size().height()}")
            if self.tabWidget.currentIndex() == 0:
                self.refreshTable()
            if self.tabWidget.currentIndex() == 1:
                updateRepkgData(self.tableWidget_repkg, False)
        self.windowDebouncer = Debouncer(resizeWindow, 350)

        # tab页切换
        def tabChange():
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
        self.tabWidget.currentChanged.connect(tabChange)

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
        self.checkBox_folders.clicked.connect(lambda event: setConfig("isFolders", not event)) # 分类文件夹锁定

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
        self.workshop = [] # 工坊数据
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
        self.captureStart = None
        self.captureEnd = None
        self.colMax = 5

        if not config['mklinkList'][0]["path"] or not config['mklinkList'][1]["path"]:
            self.tableWidget_main.setVisible(False)
            return

        self.label_error.setVisible(False)
        self.tableWidget_main.horizontalHeader().setStretchLastSection(True) # 表格自适应
        # self.tableWidget_main.horizontalHeader().setVisible(False) # 隐藏头
        # self.tableWidget_main.verticalHeader().setVisible(False) # 隐藏侧边
        self.tableWidget_main.resizeColumnsToContents() # 列宽自动调整

        def handleInvalidClick():
            print("删除失效按钮")
            openMessageDialog("备份的可以，工坊的删了还会下载回来，需要上号取消空白订阅")
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
            # print(f"筛选组 来源 类型 {event.keyType} {event.isChecked()}")
            self.sort[event.keyType] = event.isChecked()
            setConfig(event.keyType, event.isChecked())
            with timer("加载列表耗时"):
                self.filterData()
        self.buttonGroup_type.buttonClicked.connect(handleGroupFilter) # 类型
        self.buttonGroup_source.buttonClicked.connect(handleGroupFilter) # 来源
        self.checkBox_scene.keyType = "isCheckedScene"
        self.checkBox_video.keyType = "isCheckedVideo"
        self.checkBox_web.keyType = "isCheckedWeb"
        self.checkBox_application.keyType = "isCheckedApplication"
        self.checkBox_scene.setChecked(self.sort["isCheckedScene"])
        self.checkBox_video.setChecked(self.sort["isCheckedVideo"])
        self.checkBox_web.setChecked(self.sort["isCheckedWeb"])
        self.checkBox_application.setChecked(self.sort["isCheckedApplication"])
        self.checkBox_wallpaper.keyType = "isCheckedWallpaper"
        self.checkBox_backup.keyType = "isCheckedBackup"
        self.checkBox_invalid.keyType = "isCheckedInvalid"
        self.checkBox_wallpaper.setChecked(self.sort["isCheckedWallpaper"])
        self.checkBox_backup.setChecked(self.sort["isCheckedBackup"])
        self.checkBox_invalid.setChecked(self.sort["isCheckedInvalid"])

        # 排序选择
        self.comboBox_sort.setCurrentIndex(4)
        def handleSortSelect(index):
            self.sort["sortCurrent"] = self.sortCurrent[index]
            setConfig("sortCurrent", self.sort["sortCurrent"])
            # print(f'排序选择 index:{index} sortCurrent:{self.sort["sortCurrent"]}')
            self.sortData()
            self.captureData()
        self.comboBox_sort.currentIndexChanged.connect(handleSortSelect)

        # 排序
        def handleGroupSort(event):
            keyType = event.keyType == 'reverse'
            if self.sort["sortReverse"] == keyType:
                return
            # print(f"排序 keyType:{event.keyType}")
            self.sort["sortReverse"] = keyType
            setConfig("sortReverse", self.sort["sortReverse"])
            self.sortData()
            self.captureData()
        self.buttonGroup_sort.buttonClicked.connect(handleGroupSort) # 排序
        self.radioButton_positive.keyType = 'positive'
        self.radioButton_reverse.keyType = 'reverse'

        # 查看大小
        def handleGroupImg(event):
            if self.sort["displaySize"] == event.keyType:
                return
            print(f"查看大小 keyType:{event.keyType}")
            self.sort["displaySize"] = event.keyType
            setConfig("displaySize", self.sort["displaySize"])
            self.refreshTable()
        self.buttonGroup_img.buttonClicked.connect(handleGroupImg) # 查看大小
        self.radioButton_big.keyType = 240
        self.radioButton_small.keyType = self.sort["displaySize"] # 默认大小

        # 页面显示数量选择
        self.comboBox_size.setCurrentIndex(2)
        def handleSizeSelect(index):
            self.sort["filterSize"] = self.filterSize[index]
            setConfig("filterSize", self.sort["filterSize"])
            # print(f'页面显示数量选择 index:{index} filterSize:{self.sort["filterSize"]}')
            self.calculateQuantityTotal() # 刷新页面数量
        self.comboBox_size.currentIndexChanged.connect(handleSizeSelect)

        # 页选择
        def handlePageSelect(index):
            self.page = index + 1
            # print(f"页选择 index:{index} page:{self.page}")
            # 重绘翻页按钮
            if self.page >= self.total_page:
                # print("页选择redrawBtnRight no self.page:", self.page)
                self.btn_right.setVisible(False)
            else:
                # print("页选择redrawBtnRight ok self.page:", self.page)
                self.btn_right.setVisible(True)
            if self.page <= 1:
                # print("页选择redrawBtnLeft no self.page:", self.page)
                self.btn_left.setVisible(False)
                self.comboBox_page.setVisible(self.total_page != 0)
            else:
                # print("页选择redrawBtnLeft ok self.page:", self.page)
                self.btn_left.setVisible(True)
            self.captureData()
        self.comboBox_page.currentIndexChanged.connect(handlePageSelect)
        # 页切换按钮
        def handleGroupPage(event):
            print(f"页切换按钮 {event.keyType} {self.page} {type(self.page)}")
            num = self.page
            if event.keyType == 'add':
                num += 1
            elif event.keyType == 'sub':
                num -= 1
            self.comboBox_page.setCurrentIndex(num - 1) # 关联页选择,触发数据刷新
        self.buttonGroup_page.buttonClicked.connect(handleGroupPage) # 页左右切
        self.btn_left.keyType = "sub"
        self.btn_right.keyType = "add"
        self.btn_left.setVisible(False)

        # 黑名单关联
        def handleAuthorblockClick(isChecked):
            print(f"黑名单关联 {isChecked}")
            self.sort["isCheckedAuthorblock"] = isChecked
            setConfig("isCheckedAuthorblock", isChecked)
        self.checkBox_authorblock.clicked.connect(handleAuthorblockClick)
        self.checkBox_authorblock.keyType = "isCheckedAuthorblock"
        self.checkBox_authorblock.setChecked(self.sort["isCheckedAuthorblock"])

    # 加载数据
    def loadData(self, isFirst = False):
        print('loadData')
        self.page = 1
        self.workshop = getWorkshop()
        if isFirst:
            # 计算总数量和总容量（计算一次）
            total_capacity = 0
            for obj in self.workshop:
                # print(f'{obj["workshopid"]} : {obj["filesize"]}')
                total_capacity += obj["filesize"]
            self.label_capacity.setText(f"容量：{dirSizeToStr(total_capacity)}")
            self.total_size = len(self.workshop)
            print(f"工坊壁纸缓存合未知项目总数量：{self.total_size}  总容量：{total_capacity}")
        self.filterData()

    # 筛选数据
    def filterData(self):
        # 筛选来源
        def filterSource(obj):
            # 筛选失效
            def filterInvalid():
                nonlocal obj
                if obj["invalid"]:
                    return self.sort["isCheckedInvalid"]
                else:
                    return True
            # 筛选类型
            def filterType():
                nonlocal obj
                if "type" in obj:
                    keyType = obj["type"].lower()
                    if self.sort["isCheckedScene"] and keyType == "scene":
                        return filterInvalid()
                    elif self.sort["isCheckedVideo"] and keyType == "video":
                        return filterInvalid()
                    elif self.sort["isCheckedWeb"] and keyType == "web":
                        return filterInvalid()
                    elif self.sort["isCheckedApplication"] and keyType == "application":
                        return filterInvalid()
                    elif keyType == "dir":
                        return filterInvalid()
                return False
            try:
                keySource = obj["source"].lower()
                # if keySource == "wallpaper":
                #     if self.sort["isCheckedWallpaper"]:
                #         return filterType()
                #     else:
                #         return False
                # elif keySource == "backup":
                
                if self.sort["isCheckedWallpaper"] and keySource == "wallpaper":
                    if self.sort["isCheckedInvalid"] and obj["invalid"]:
                        return True
                    else:
                        return filterType()
                elif self.sort["isCheckedBackup"] and keySource == "backup":
                    if self.sort["isCheckedInvalid"] and obj["invalid"]:
                        return True
                    else:
                        return filterType()
                elif not self.sort["isCheckedWallpaper"] and not self.sort["isCheckedBackup"]:
                    return self.sort["isCheckedInvalid"] and obj["invalid"]
            except Exception as e:
                logging.error(f"筛选来源{e}: {obj}")
            # if config['isDevelopment']:
            #     print(f'不符合筛选排除: {obj["source"]} {obj["workshopid"]}')
            return False
        # print(f"筛选前长度：{len(self.workshop)}")
        self.data = list(filter(filterSource, self.workshop))
        self.filter_total_size = len(self.data) # 筛选后长度
        self.label_filter.setText(f"筛选结果（ {self.total_size} 个中有 {self.filter_total_size} 个）")
        self.calculateQuantityTotal()

    # 重新计算总页数
    def calculateQuantityTotal(self):
        self.total_page = math.ceil(self.filter_total_size / self.sort["filterSize"])
        self.label_page.setText(f"共 {self.total_page} 页")
        print('重新计算总页数calculateQuantityTotal: ', self.total_page)
        model = QStringListModel()
        pageData = []
        for i in range(0, self.total_page):
            pageData.append(str(i+1))
        model.setStringList(pageData)
        self.comboBox_page.setModel(model) # 会触发刷新数据

    # 排序列表数据
    def sortData(self):
        print(f'设置列表数据sortData {len(self.data)}')
        # 排序(除了名称倒序，其他都是正序)
        self.data.sort(key=lambda x:x[self.sort["sortCurrent"]], reverse = self.sort["sortReverse"])
    
    # 截取列表数据
    def captureData(self):
        # 截取
        self.captureStart = (self.page - 1) * self.sort["filterSize"]
        self.captureEnd = self.page * self.sort["filterSize"]
        if self.captureEnd > self.filter_total_size:
            self.captureEnd = None
        self.refreshTable()

    # 刷新列表
    def refreshTable(self):
        # 重新计算图文宽度和最大列数
        def calculateQuantityImgsizeCol(widgetWidth, colMax):
            imgWidth = int(widgetWidth / colMax)
            if imgWidth > self.sort["displaySize"]:
                imgWidth, colMax = calculateQuantityImgsizeCol(widgetWidth, colMax + 1)
            # elif imgWidth < 180:
            #     colMax = colMax - 1
            #     imgWidth, _ = calculateQuantityImgsizeCol(widgetWidth, colMax)
            return imgWidth, colMax
        imgWidth, self.colMax = calculateQuantityImgsizeCol(self.tableWidget_main.size().width() - 16, 3)
        print('重新计算图文宽度和最大列数', imgWidth, self.colMax)

        self.tableWidget_main.clearContents() # 清空
        if self.total_page == self.page:
            self.tableWidget_main.setRowCount(math.ceil(self.filter_total_size % self.sort["filterSize"] / self.colMax))
        else:
            self.tableWidget_main.setRowCount(math.ceil(self.sort["filterSize"] / self.colMax))
        self.tableWidget_main.setRowHeight(0, imgWidth)

        self.tableWidget_main.setColumnCount(self.colMax)
        # 根据列数设置列宽
        i = 0
        while i < self.colMax:
            self.tableWidget_main.setColumnWidth(i, imgWidth)
            i += 1
        
        # 重绘单元格
        def redrawItem(imgPath, name):
            nonlocal imgWidth
            itemBox = QLabel()
            # itemBox.setMinimumSize(QSize(size, size))
            itemBox.setMaximumSize(QSize(imgWidth, imgWidth))
            # itemBox.setScaledContents(True)
            itemBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
            itemBox.setPixmap(QPixmap(imgPath).scaled(imgWidth, imgWidth, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            return itemBox
        
        row = 0 # 计数行
        col = 0 # 计数列
        for item in self.data[self.captureStart:self.captureEnd]: # 截取功能要浅拷贝处理，否则会加载上次截取
            self.tableWidget_main.setCellWidget(row, col, redrawItem(item["previewsmall"], item["title"]))
            col += 1
            if col >= self.colMax:
                col = 0
                row += 1
                self.tableWidget_main.setRowHeight(row, imgWidth)

    # 初始化界面右侧功能
    def initMainRight(self):
        self.currentItem = None

        # self.label_img.setVisible(False)
        self.label_name.setVisible(False)
        self.label_title.setVisible(False)
        self.label_note.setVisible(False)
        self.groupBox_btn.setVisible(False)

        def get_type_str(key):
            keyType = key.lower()
            typeStr = "未知"
            if keyType == "scene":
                typeStr = "场景"
            elif keyType == "video":
                typeStr = "视频"
            elif keyType == "web":
                typeStr = "网页"
            elif keyType == "application":
                typeStr = "应用"
            return typeStr
        
        # 表格点击（重复点击不会触发）
        def handleTableMainChange(row, col):
            item = self.data[row * self.colMax + col]
            if item == None:
                return
            # 首次点击
            if self.currentItem == None:
                self.label_error_project.setVisible(False)
                # self.label_img.setVisible(True)
                self.label_name.setVisible(True)
                self.label_title.setVisible(True)
                self.label_note.setVisible(True)
                self.groupBox_btn.setVisible(True)
            self.currentItem = item
            # itemBox.setMaximumSize(QSize(imgWidth, imgWidth))
            # itemBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label_img.setPixmap(QPixmap(self.currentItem["previewsmall"]).scaled(182, 182, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.label_name.setText(self.currentItem["workshopid"])
            self.label_title.setText(self.currentItem["title"])
            self.label_type.setText(f'【{get_type_str(self.currentItem["type"])}】 {self.currentItem["filesizelabel"]}')
            self.label_subscriptiondate.setText(time.strftime("订阅时间：%Y-%m-%d %X", time.localtime(self.currentItem["subscriptiondate"])))
            self.label_updatedate.setText(time.strftime("更新时间：%Y-%m-%d %X", time.localtime(self.currentItem["updatedate"])))
            if "description" in self.currentItem:
                self.label_note.setText(self.currentItem["description"])
            else:
                try:
                    with open(self.currentItem["project"], encoding="utf-8") as f1:
                        data = json.load(f1)
                        self.label_note.setText(data["description"] if "description" in data else "简介：无")
                except Exception as e:
                    logging.warning(f"读取config.json: {e}")
            if self.currentItem["type"].lower() == 'scene':
                self.btn_repkg_work.setVisible(True)
                self.btn_repkg_dir.setVisible(True)
            else:
                self.btn_repkg_work.setVisible(False)
                self.btn_repkg_dir.setVisible(False)
            if self.currentItem["source"] == 'backup':
                self.btn_capacity.setVisible(True)
            else:
                self.btn_capacity.setVisible(False)
            # print('表格点击', row, col, self.currentItem)
        self.tableWidget_main.cellClicked.connect(handleTableMainChange)
        # 打开资源管理器
        def handleDirOpen():
            os.startfile(os.path.dirname(self.currentItem["project"]))
        self.btn_open.clicked.connect(handleDirOpen)
        def handleEdit():
            openMessageDialog("开发中")
            print("修改按钮")
            # 备份文件夹单个项目，\n每次修改更新时间戳，\n大小计算
        self.btn_edit.clicked.connect(handleEdit)
        # 重新计算大小按钮
        def handleCapacity():
            self.currentItem["filesize"] = getDirSize(os.path.dirname(self.currentItem["project"]))
            self.currentItem["filesizelabel"] = dirSizeToStr(self.currentItem["filesize"])
            print("重新计算大小按钮", self.currentItem["filesizelabel"])
            self.label_type.setText(f'【{get_type_str(self.currentItem["type"])}】 {self.currentItem["filesizelabel"]}')
            for item in config["workshopBackup"]:
                if item["workshopid"] == self.currentItem["workshopid"]:
                    item["filesize"] = self.currentItem["filesize"]
                    item["filesizelabel"] = self.currentItem["filesizelabel"]
                    break
        self.btn_capacity.clicked.connect(handleCapacity)
        # 提取repkg
        def handleRepkgWork():
            splitext = os.path.splitext(self.currentItem["file"])
            __path = self.currentItem["file"]
            if splitext[1].lower() != '.pkg':
                __path = splitext[0] + '.pkg'
                if not os.path.exists(__path):
                    openMessageDialog("无法找到pkg文件")
                    return
            if runRepkg(__path):
                if followWork():
                    # updateRepkgData(self.tableWidget_repkg)
                    setConfig('repkgPath', __path)
        self.btn_repkg_work.clicked.connect(handleRepkgWork)
        # 打开repkg output
        def handleRepkgDir():
            os.startfile(os.path.join(os.getcwd(), "output"))
        self.btn_repkg_dir.clicked.connect(handleRepkgDir)

    # repkg初始化
    def initRepkg(self):
        self.tableWidget_repkg.horizontalHeader().setStretchLastSection(True) # 表格自适应
        # self.tableWidget_repkg.horizontalHeader().setVisible(True) # 隐藏头
        # self.tableWidget_repkg.verticalHeader().setVisible(True) # 隐藏侧边

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

        def handleRepkgDir():
            # 打开资源管理器
            os.startfile(os.path.join(os.getcwd(), "output"))
        self.btn_repkg_output.clicked.connect(handleRepkgDir)

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

    # 黑名单初始化
    def initAuthorblock(self):
        self.virus = []

        # 黑名单列表点击
        def handleAuthorblockClick():
            obj = temp_authorblocklistnames[self.listWidget_authorblock.currentRow()]
            openMessageDialog("已复制到剪贴板")
            pyperclip.copy(f"名称: {obj['name']}{os.linesep}ID: {obj['value']}")
        self.listWidget_authorblock.itemClicked.connect(handleAuthorblockClick)
        # 毒狗列表点击
        def handleVirusClick():
            obj = self.virus[self.listWidget_virus.currentRow()]
            openMessageDialog("已复制到剪贴板")
            pyperclip.copy(f"名称: {obj['personaname']}{os.linesep}profileurl: {obj['profileurl']}")
        self.listWidget_virus.itemClicked.connect(handleVirusClick)
        # 域名生成steamworks key
        self.btn_authorblock_new.clicked.connect(lambda: openMessageDialog("404 域名没啦"))
        # 传入steamid列表 返回查询基本信息
        # https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/
        self.btn_authorblock_refresh.clicked.connect(lambda: openMessageDialog("steamworks key 失效"))

    # 黑名单列表数据加载
    def get_addauthorblock_list(self):
        if len(temp_authorblocklistnames) != self.listWidget_authorblock.count():
            print('黑名单列表加载数据')
            for item in temp_authorblocklistnames:
                self.listWidget_authorblock.addItem(f"名称: {item['name']}{os.linesep}ID: {item['value']}")
        
        if not self.listWidget_virus.count():
            try:
                path = os.path.join(os.getcwd(), 'authorblock')
                if os.path.exists(path):
                    with open(os.path.join(path, 'authorblock.json'), encoding="utf-8") as f1:
                        self.virus = json.load(f1)
                        # print(data)
                        print('毒狗列表加载数据')
                        self.listWidget_virus.setIconSize(QSize(48, 48))
                        for item in self.virus:
                            strIsBlock = ""
                            for obj in temp_authorblocklistnames:
                                if obj["value"] == item["steamid"]:
                                    strIsBlock = "【已拉黑】"
                                    break
                            note = f'{item["steamid"]}{strIsBlock}{os.linesep}目前名字：{item["personaname"]}{os.linesep}{" // ".join(item["realname"])}'
                            # print(os.path.join(os.getcwd(), 'authorblock', item["avatarmedium"]))
                            icon = QPixmap(os.path.join(os.getcwd(), 'authorblock', item["avatarmedium"]))
                            icon.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            item = QListWidgetItem(icon, note)
                            self.listWidget_virus.addItem(item)
            except Exception as e:
                logging.warning(f"读取authorblock.json: {e}")

    # 窗口变化
    def resizeEvent(self, event):
        if self.windowWidth == self.size().width():
            return
        self.windowDebouncer.trigger()


if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()
