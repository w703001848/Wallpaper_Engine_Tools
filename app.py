import os, sys, subprocess, atexit, pyperclip
import logging, math, time, json
# PySide6组件调用
from PySide6.QtCore import Qt, QSize, QStringListModel
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QMenu, QListWidgetItem, QInputDialog
# 加载模板
from widgets.Ui_main import Ui_MainForm
from widgets.itemImg import ItemImg
# 功能模块
from modules.main import Debouncer, timer, convert_path, Unlock_hidden_achievements, getDirSize, dirSizeToStr, openFileDialog, openDirDialog, openMessageDialog, openStartfile, dragEnterEvent
from modules.Config import config, temp_authorblocklistnames, get_wallpaper_config, getWorkshop, getBackup, getTemp, setSteamPath, setWallpaperPath, setWallpaperBackupPath, setConfig, saveConfig
from modules.RePKG import runRepkg, followWork, updateRepkgData
from modules.Mklink import mklinkCreate, mklinkNew, mklinkBack, updateMklinkList
from modules.Storege import MoveProject, GeneratedDirNas, GeneratedDirThread
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
            self.initContextMenu()
            self.initMain()
            self.initMainRight()
            self.initRepkg()
            self.initMklink()
            self.initNaslink()
            self.initAuthorblock()
            self.initVirus()
            self.initTemp()

            # 加载数据
            self.loadData()

        # 打包-加载画面 关闭
        try:
            import pyi_splash
            pyi_splash.close()
        except ImportError:
            pass

    def initPage(self): # 初始化界面
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
                self.get_nas_list()
            elif index == 3: # 黑名单加载
                self.get_authorblock_list()
                self.get_virus_list()
                self.get_temp_list()
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

        # 调用此函数以重启应用
        def showRestartConfirmation():
            if openMessageDialog("清空缓存数据并重启，请确认！", "tip"):
                # setConfig("isCheckedScene", True) # 场景
                # setConfig("isCheckedVideo", True) # 视频
                # setConfig("isCheckedWeb", True) # 网页
                # setConfig("isCheckedApplication", True) # 应用
                # setConfig("filterSize", 30) # 分页
                # setConfig("sortCurrent", "subscriptiondate") # 订阅日期
                # setConfig("isCheckedInvalid", True) # 失效
                # 获取当前脚本的路径
                script_path = sys.argv[0]
                # 获取当前脚本的目录，以防脚本不在工作目录中
                script_dir = os.path.dirname(os.path.realpath(script_path))
                # 使用subprocess启动新进程，传递所有命令行参数
                subprocess.Popen([sys.executable, script_path] + sys.argv[1:])
                # 退出当前进程
                sys.exit(0)
        self.btn_restart.clicked.connect(showRestartConfirmation) # 清空缓存重启

    def initMain(self): # 初始化壁纸
        self.workshop = [] # 工坊数据
        self.backup = [] # 备份数据
        self.tempData = [] # 临时存放数据
        self.total_data = 0 # 总项目数量
        self.total_capacity = {
            "workshop": "",
            "backup": "",
            "tempData": "",
        } # 项目容量
        self.folders = [] # 当前文件夹
        self.folders_index = [] # 当前文件夹选择
        self.folders_size = 0 # 当前文件夹数量
        self.data = [] # 列表数据
        self.folders_data = []
        self.filter_data = []
        self.page = 1 # 当前页
        self.total_page = 1 # 总页数
        self.total_size = 0 # 总数量
        self.captureStart = None
        self.captureEnd = None
        self.colMax = 5
        self.filterSize = [10, 20, 30, 50]
        self.sortCurrent = ["title", "ratingrounded", "favorite", "filesize", "subscriptiondate", "updatedate"]
        self.sort = {
            "isCheckedScene": config["isCheckedScene"],
            "isCheckedVideo": config["isCheckedVideo"],
            "isCheckedWeb": config["isCheckedWeb"],
            "isCheckedApplication": config["isCheckedApplication"],
            "sortCurrent": config["sortCurrent"], # 订阅日期: subscriptiondate
            "sortReverse": config["sortReverse"], # 排序 正序
            "filterSize": config["filterSize"], # 筛选数量
            "displaySize": config["displaySize"], # 显示大小
        }

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
            self.filterData()
        self.btn_search.clicked.connect(handleSearchClick)
        
        self.btn_clear.setVisible(False)
        def handleSearchClearClick():
            self.lineEdit_search.setText("")
            print("清空查询文本")
            self.btn_clear.setVisible(False)
            self.filterData()
        self.btn_clear.clicked.connect(handleSearchClearClick)

        # 筛选组 类型
        self.checkBox_scene.setChecked(self.sort["isCheckedScene"])
        self.checkBox_video.setChecked(self.sort["isCheckedVideo"])
        self.checkBox_web.setChecked(self.sort["isCheckedWeb"])
        self.checkBox_application.setChecked(self.sort["isCheckedApplication"])
        self.checkBox_scene.keyType = "isCheckedScene"
        self.checkBox_video.keyType = "isCheckedVideo"
        self.checkBox_web.keyType = "isCheckedWeb"
        self.checkBox_application.keyType = "isCheckedApplication"
        def handleGroupFilter(event):
            # print(f"筛选组 来源 类型 {event.keyType} {event.isChecked()}")
            self.sort[event.keyType] = event.isChecked()
            setConfig(event.keyType, event.isChecked())
            self.filterData()
        self.buttonGroup_type.buttonClicked.connect(handleGroupFilter) # 类型
        
        # 来源组 类型
        self.checkBox_wallpaper.setChecked(config["isCheckedWallpaper"])
        self.checkBox_backup.setChecked(config["isCheckedBackup"])
        self.checkBox_temp.setChecked(config["isCheckedTemp"])
        self.checkBox_wallpaper.keyType = "isCheckedWallpaper"
        self.checkBox_backup.keyType = "isCheckedBackup"
        self.checkBox_temp.keyType = "isCheckedTemp"
        def handleGroupSource(event):
            # print(f"筛选组 来源 类型 {event.keyType} {event.isChecked()}")
            setConfig(event.keyType, event.isChecked())
            self.loadData()
        self.buttonGroup_source.buttonClicked.connect(handleGroupSource) # 来源

        # 排序选择
        for i, key in enumerate(self.sortCurrent):
            if self.sort["sortCurrent"] == key:
                self.comboBox_sort.setCurrentIndex(i)
                break
        def handleSortSelect(index):
            self.sort["sortCurrent"] = self.sortCurrent[index]
            setConfig("sortCurrent", self.sort["sortCurrent"])
            # print(f'排序选择 index:{index} sortCurrent:{self.sort["sortCurrent"]}')
            self.sortData()
        self.comboBox_sort.currentIndexChanged.connect(handleSortSelect)

        # 排序
        if self.sort["sortReverse"]:
            self.radioButton_reverse.setChecked(True)
        else:
            self.radioButton_positive.setChecked(True)
        self.radioButton_positive.keyType = 'positive'
        self.radioButton_reverse.keyType = 'reverse'
        def handleGroupSort(event):
            keyType = event.keyType == 'reverse'
            if self.sort["sortReverse"] == keyType:
                return
            # print(f"排序 keyType:{event.keyType}")
            self.sort["sortReverse"] = keyType
            setConfig("sortReverse", self.sort["sortReverse"])
            self.sortData()
        self.buttonGroup_sort.buttonClicked.connect(handleGroupSort) # 排序

        # 查看大小
        if self.sort["displaySize"] == 240:
            self.radioButton_big.setChecked(True)
        else:
            self.radioButton_small.setChecked(True)
        self.radioButton_big.keyType = 240
        self.radioButton_small.keyType = 160 # 默认大小
        def handleGroupImg(event):
            if self.sort["displaySize"] == event.keyType:
                return
            # print(f"查看大小 keyType:{event.keyType}")
            self.sort["displaySize"] = event.keyType
            setConfig("displaySize", self.sort["displaySize"])
            self.refreshTable()
        self.buttonGroup_img.buttonClicked.connect(handleGroupImg) # 查看大小

        # 页面显示数量选择
        for i, key in enumerate(self.filterSize):
            if self.sort["filterSize"] == key:
                self.comboBox_size.setCurrentIndex(i)
                break
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
        self.btn_left.setVisible(False)
        self.btn_left.keyType = "sub"
        self.btn_right.keyType = "add"
        def handleGroupPage(event):
            print(f"页切换按钮 {event.keyType} {self.page} {type(self.page)}")
            num = self.page
            if event.keyType == 'add':
                num += 1
            elif event.keyType == 'sub':
                num -= 1
            self.comboBox_page.setCurrentIndex(num - 1) # 关联页选择,触发数据刷新
        self.buttonGroup_page.buttonClicked.connect(handleGroupPage) # 页左右切

        # 分类文件夹锁定
        self.checkBox_folders.setChecked(config["isCheckedFolders"])
        def setFoloders(event):
            setConfig("isCheckedFolders", event)
            if event:
                get_wallpaper_config()
            self.loadData()
        self.checkBox_folders.clicked.connect(setFoloders) 

        # 失效壁纸显示
        self.checkBox_invalid.setChecked(config["isCheckedInvalid"])
        def setInvalid(event):
            setConfig("isCheckedInvalid", event)
            self.filterData()
        self.checkBox_invalid.clicked.connect(setInvalid) 

        # 黑名单关联
        self.checkBox_authorblock.setChecked(config["isCheckedAuthorblock"])
        def setAuthorblock(event):
            setConfig("isCheckedAuthorblock", event)
            self.refreshTable()
        self.checkBox_authorblock.clicked.connect(setAuthorblock) 

        self.progressBar.setVisible(False)

    def loadData(self): # 加载数据
        if not config['wallpaperPath']:
            return
        print('loadData')
        if len(self.workshop) == 0:
            self.workshop = getWorkshop()
        if len(self.backup) == 0:
            self.backup = getBackup()
        if len(self.tempData) == 0:
            self.tempData = getTemp()

        self.data = []
        self.page = 1

        # 计算总总容量
        def totalCapacity(key, data):
            if self.total_capacity[key] == "":
                capacity = 0
                for obj in data:
                    # print(f'{obj["workshopid"]} : {obj["filesize"]}')
                    capacity += obj["filesize"]
                self.total_capacity[key] = capacity
            return self.total_capacity[key]
        
        total_capacity = 0
        self.total_data = 0
        if config["isCheckedWallpaper"]:
            self.data += self.workshop
            self.total_data += len(self.workshop)
            total_capacity += totalCapacity("workshop", self.workshop)
        if config["isCheckedBackup"]:
            self.data += self.backup
            self.total_data += len(self.backup)
            total_capacity += totalCapacity("backup", self.backup)
        if config["isCheckedTemp"]:
            self.data += self.tempData
            self.total_data += len(self.tempData)
            total_capacity += totalCapacity("tempData", self.tempData)
        self.label_capacity.setText(f"容量：{dirSizeToStr(total_capacity)}")
        print(f"项目总数量：{self.total_data}  {self.label_capacity.text()}")

        # 生成文件夹数据并标记self.data
        if config["isCheckedFolders"]:
            if not len(self.folders):
                # 生成folders 查询self.data 标记layer
                def mergeFolder(data, folders, layer):
                    for i, obj in enumerate(data):
                        folders.append({
                            "layer" : f"{i}" if layer == "" else f"{layer},{i}",
                            "subfolders" : [],
                            "title" : obj["title"],
                            "previewsmall": u":/img/dir.png",
                            "invalid": False,
                            "steamid": "",
                            "type" : "folder"
                        })
                        for key in obj["items"].keys():
                            if len(key) < 15:
                                for item in self.workshop:
                                    if item["workshopid"] == key:
                                        item["layer"] = folders[i]["layer"]
                                        # print("layer", item["workshopid"], item["layer"])
                                        break
                            else:
                                for item in self.backup:
                                    if key.find(item["workshopid"]) != -1:
                                        item["layer"] = folders[i]["layer"]
                                        # print("layer2", item["workshopid"], item["layer"])
                                        break
                        if len(obj["subfolders"]):
                            mergeFolder(obj["subfolders"], folders[i]["subfolders"], folders[i]["layer"])
                self.folders = {
                    "layer" : "",
                    "subfolders" : [],
                    "title" : "首页",
                    "previewsmall": u":/img/dir.png",
                    "invalid": False,
                    "steamid": "",
                    "type" : "folder"
                }
                mergeFolder(config["folders"], self.folders["subfolders"], self.folders["layer"])

        self.sortData()

    def sortData(self): # 排序列表数据
        print(f'排序sortData: {len(self.data)}')
        # 排序(除了名称倒序，其他都是正序)
        self.data.sort(key=lambda x:x[self.sort["sortCurrent"]], reverse = self.sort["sortReverse"])

        self.foldersData()

    def foldersData(self): # 筛选文件夹数据
        self.folders_size = 0
        self.folders_data = []
        if config["isCheckedFolders"]:
            # # 获取文件夹展开层级数据
            folders = []
            # 生成文件夹头部
            if len(self.folders_index):
                folders = [{
                    "layer" : "",
                    "subfolders" : [],
                    "title" : "返回",
                    "previewsmall": u":/img/dir.png",
                    "invalid": True,
                    "steamid": "",
                    "type" : "folder"
                }]
                data = self.folders["subfolders"]
                for i in self.folders_index:
                    data = data[i]["subfolders"]
                folders += data
            else:
                folders = self.folders["subfolders"]
            self.folders_size = len(folders)
            print("生成folders", self.folders_size)
            foldersIndex = ",".join('%s' %item for item in self.folders_index)
            if foldersIndex == "":
                self.folders_data = folders + list(filter(lambda item: "layer" not in item, self.data))
            else:
                self.folders_data = folders + list(filter(lambda item: "layer" in item and item["layer"] == foldersIndex, self.data))
        else:
            self.folders_data = self.data
        self.filterData()

    def filterData(self): # 筛选类型数据
        isCheckedInvalid = config["isCheckedInvalid"] and not self.sort["isCheckedScene"] and not self.sort["isCheckedVideo"] and not self.sort["isCheckedWeb"] and not self.sort["isCheckedApplication"]
        # 筛选来源
        def filterType(obj):
            nonlocal isCheckedInvalid
            # 筛选失效
            def filterInvalid():
                nonlocal obj
                if obj["invalid"]:
                    return config["isCheckedInvalid"]
                else:
                    return True
            # 筛选类型
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
                elif keyType == "folder":
                    return True
                elif isCheckedInvalid:
                    return obj["invalid"]
            # if config['isDevelopment']:
            #     print(f'不符合筛选排除: {obj["source"]} {obj["workshopid"]}')
            return False
        print(f"筛选filterTypeData: {len(self.folders_data)}")
        self.filter_data = list(filter(filterType, self.folders_data))
        self.total_size = len(self.filter_data) # 筛选后长度
        self.label_filter.setText(f"筛选结果（ {self.total_data} 个中有 {self.total_size - self.folders_size} 个）")
        self.calculateQuantityTotal()

    def calculateQuantityTotal(self): # 重新计算总页数
        self.total_page = math.ceil(self.total_size / self.sort["filterSize"])
        self.label_page.setText(f"共 {self.total_page} 页")
        print('重置总页数calculateQuantityTotal: ', self.total_page)
        model = QStringListModel()
        pageData = []
        for i in range(0, self.total_page):
            pageData.append(str(i+1))
        model.setStringList(pageData)
        self.comboBox_page.setModel(model) # 会触发刷新数据
    
    def captureData(self): # 截取列表数据
        # 截取
        self.captureStart = (self.page - 1) * self.sort["filterSize"]
        self.captureEnd = self.page * self.sort["filterSize"]
        if self.captureEnd > self.total_size:
            self.captureEnd = None
        print(f'截取captureData: {self.captureStart} - {self.captureEnd}')
        self.refreshTable()

    def refreshTable(self): # 刷新列表
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
            self.tableWidget_main.setRowCount(math.ceil((self.total_size - (self.sort["filterSize"] * (self.page - 1))) / self.colMax))
        else:
            self.tableWidget_main.setRowCount(math.ceil(self.sort["filterSize"] / self.colMax))
        self.tableWidget_main.setRowHeight(0, imgWidth)

        self.tableWidget_main.setColumnCount(self.colMax)
        # 根据列数设置列宽
        i = 0
        while i < self.colMax:
            self.tableWidget_main.setColumnWidth(i, imgWidth)
            i += 1

        row = 0 # 计数行
        col = 0 # 计数列
        for item in self.filter_data[self.captureStart:self.captureEnd]: # 截取功能要浅拷贝处理，否则会加载上次截取
            # 绘制单元格
            widget = ItemImg()
            # 黑名单匹配
            isAuthorblock = False
            if config["isCheckedAuthorblock"] and item.get("authorsteamid"):
                for obj in self.virus:
                    if obj["steamid"] == item["authorsteamid"]:
                        print(f'黑名单匹配: {obj["personaname"]} {"*" * 100}')
                        item["title"] = f'黑名单【{obj["personaname"]}】{item["title"]}'
                        isAuthorblock = True
                        break
            widget.setContent(imgWidth, item["previewsmall"], item["title"], isAuthorblock, item['invalid'])
            self.tableWidget_main.setCellWidget(row, col, widget)
            col += 1
            if col >= self.colMax:
                col = 0
                row += 1
                self.tableWidget_main.setRowHeight(row, imgWidth)

    def initContextMenu(self): # 右键弹窗初始化
        self.itemMenu = None
        # 右键弹窗
        self.context_menu = QMenu(self)
        self.copyTitle = self.context_menu.addAction("标题复制")
        def handleCopyTitle():
            pyperclip.copy(self.itemMenu["title"])
            # openMessageDialog("已复制到剪贴板")
        self.copyTitle.triggered.connect(handleCopyTitle)
        self.actionStartfile = self.context_menu.addAction("打开资源管理器")
        def handleStartfile():
            os.startfile(os.path.dirname(self.itemMenu["project"]))
        self.actionStartfile.triggered.connect(handleStartfile)

        # self.context_menu.addSeparator() # 分割线
        # self.actionEdit = self.context_menu.addAction("修改")

        self.actionMoveBackup = self.context_menu.addAction("转移备份")
        def handleMoveBackup():
            # self.progressBar.setVisible(True)
            # self.progressBar.setRange(0,0)
            # MoveProject(self.itemMenu)
            # self.progressBar.setVisible(False)
            # 多线程
            if not GeneratedDirThread.paused:
                GeneratedDirThread.setFun(lambda: MoveProject(self.itemMenu))
                GeneratedDirThread.start()
        self.actionMoveBackup.triggered.connect(handleMoveBackup)

        self.menuMoveNas = QMenu("转移NAS同步备份", self)
        def handleMenuNas(e):
            self.progressBar.setVisible(True)
            self.progressBar.setRange(0,0)
            for obj in config["nasLink"]:
                if obj["remark"] == e.text():
                    MoveProject(self.itemMenu, os.path.join(obj["IP"], obj["dir"]))
            self.progressBar.setVisible(False)
        self.menuMoveNas.triggered.connect(handleMenuNas)
        self.context_menu.addMenu(self.menuMoveNas)

        self.tableWidget_main.setContextMenuPolicy(Qt.CustomContextMenu) # 开启右键菜单触发
        self.tableWidget_main.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, pos): # 右键弹窗显示
        # print("右键弹窗", pos)
        # 右键指向项目
        indexAt = self.tableWidget_main.indexAt(pos)
        if indexAt.isValid():
            row, col = indexAt.row(), indexAt.column()
            index = row * self.colMax + col + (self.page - 1) * self.sort["filterSize"]
            if index >= len(self.filter_data) or index < 0:
                return
            self.itemMenu = self.filter_data[index]
            # 项目适配选项
            if self.itemMenu["type"] == "folder":
                return
            if self.itemMenu["source"] == "wallpaper":
                self.actionMoveBackup.setVisible(True)
            elif self.itemMenu["source"] == "backup":
                self.actionMoveBackup.setVisible(False)
                if self.itemMenu["storagepath"] != "":
                    self.menuMoveNas.setVisible(False)
            else:
                self.actionMoveBackup.setVisible(False)
                self.menuMoveNas.setVisible(False)
            # 更新二级菜单
            self.menuMoveNas.clear()
            for obj in config["nasLink"]:
                self.menuMoveNas.addAction(obj["remark"])
            # 显示弹窗
            self.context_menu.exec(self.tableWidget_main.viewport().mapToGlobal(pos))

    def initMainRight(self): # 初始化界面右侧功能
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
            index = row * self.colMax + col + (self.page - 1) * self.sort["filterSize"]
            if index >= len(self.filter_data) or index < 0:
                return
            item = self.filter_data[index]
            # 点击文件夹
            if item["type"] == "folder":
                # print(item, index)
                if item["title"] == "返回":
                    current = self.folders_index.pop()
                    data = self.folders["subfolders"]
                    for i in self.folders_index:
                        data = data[i]["subfolders"]
                    __index = data[current]["title"].find("-(")
                    if __index != -1:
                        data[current]["title"] = f"{data[current]['title'][:__index]}-({self.total_size - self.folders_size})"
                    else:
                        data[current]["title"] = f"{data[current]['title']}-({self.total_size - self.folders_size})"
                else:
                    if len(self.folders_index) == 0:
                        self.folders_index.append(index)
                    else:
                        self.folders_index.append(index - 1)
                print("返回foldersIndex", self.folders_index)
                self.foldersData()
                return
            # 首次点击
            elif self.currentItem == None:
                self.label_error_project.setVisible(False)
                # self.label_img.setVisible(True)
                self.label_name.setVisible(True)
                self.label_title.setVisible(True)
                self.label_note.setVisible(True)
                self.groupBox_btn.setVisible(True)
            self.currentItem = self.itemMenu = item
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
                    f1 = open(self.currentItem["project"], encoding="utf-8")
                    data = json.load(f1)
                    self.label_note.setText(data["description"] if "description" in data else "简介：无")
                    f1.close()
                except Exception as e:
                    logging.error(f"读取config.json简介: {e}")
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
                    setConfig('repkgPath', convert_path(__path))
        self.btn_repkg_work.clicked.connect(handleRepkgWork)
        # 打开repkg output
        def handleRepkgDir():
            os.startfile(os.path.join(os.getcwd(), "output"))
        self.btn_repkg_dir.clicked.connect(handleRepkgDir)

    def initRepkg(self): # repkg初始化
        self.tableWidget_repkg.horizontalHeader().setStretchLastSection(True) # 表格自适应
        # self.tableWidget_repkg.horizontalHeader().setVisible(True) # 隐藏头
        # self.tableWidget_repkg.verticalHeader().setVisible(True) # 隐藏侧边
        
        self.lineEdit_repkg.setAcceptDrops(True)
        self.lineEdit_repkg.dragEnterEvent = dragEnterEvent
        # 拖放事件释放接收
        def dropEvent(event):
            urls = event.mimeData().urls()
            if urls and urls[0].isLocalFile():
                folder_path = urls[0].toLocalFile()  # 获取文件夹路径
                if os.path.isfile(folder_path):
                    file = os.path.splitext(folder_path)
                    if file[1].lower() == '.pkg' or file[1].lower() == '.mpkg':
                        self.lineEdit_repkg.setText(folder_path)  # 显示路径
                    # event.acceptProposedAction()
        self.lineEdit_repkg.dropEvent = dropEvent

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

    def initMklink(self): # 软地址初始化
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
                self.listWidget_mklink.addItem(f"标注:{obj['remark']}\n{obj['path']}\n未生成")
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
                self.listWidget_mklink.currentItem().setText(f"标注:{obj['remark']}\n{obj['path']}\n{obj['path_new'] or '未生成'}")
                self.lineEdit_mklink_path_new.setText(obj['path_new'])
        self.btn_mklink_create.clicked.connect(handleMklinkCreateClick)

        # 还原
        def handleMklinkBackClick():
            index = self.listWidget_mklink.currentRow()
            if mklinkBack(index):
                obj = config["mklinkList"][index]
                obj['path_new'] = ""
                self.listWidget_mklink.currentItem().setText(f"标注:{obj['remark']}\n{obj['path']}\n未生成")
                self.lineEdit_mklink_path_new.setText("")
        self.btn_mklink_restore.clicked.connect(handleMklinkBackClick)

    def initNaslink(self): # NAS备份
        self.nasLink = config["nasLink"]

        def handleNasInput(e):
            if e != config["nasLinkPath"]:
                self.btn_nas_save.setVisible(True)
        self.lineEdit_nas_path_backup.textChanged.connect(handleNasInput)
        self.lineEdit_nas_path_backup.setText(config["nasLinkPath"])
        def handleNasSaveClick():
            txt = convert_path(self.lineEdit_nas_path_backup.text())
            self.lineEdit_nas_path_backup.setText(txt)
            if os.path.exists(txt):
                self.btn_nas_save.setVisible(False)
                setConfig("nasLinkPath", txt)
            else:
                openMessageDialog("地址错误！")
        self.btn_nas_save.clicked.connect(handleNasSaveClick)
        self.btn_nas_save.setVisible(False)

        def handleNewClick():
            txt = self.lineEdit_nas_path_backup.text()
            if os.path.exists(txt):
                remark, ok = QInputDialog.getText(None, '新增存储', '请输入备注 例：游戏')
                if ok:
                    path = openDirDialog(txt)
                    if path:
                        dir = path[len(txt):]
                        obj = {
                            "remark": remark,
                            "IP": txt,
                            "dir": dir
                        }
                        self.nasLink.append(obj)
                        self.listWidget_nas.addItem(f'{obj["remark"]}{os.linesep}存储位置：{obj["IP"]}  -  路径：{obj["dir"]}')
            else:
                openMessageDialog("ip地址错误！")
        self.btn_naslink_new.clicked.connect(handleNewClick)
        def handleRemoveClick():
            index = self.listWidget_nas.currentRow()
            if index >=0:
                del self.nasLink[index]
                self.listWidget_nas.takeItem(index)
                self.listWidget_nas.setCurrentRow(-1)
                self.btn_naslink_remove.setVisible(False)
            else:
                openMessageDialog("请选择需要删除的地址！")
        self.btn_naslink_remove.clicked.connect(handleRemoveClick)
        self.btn_naslink_remove.setVisible(False)
        
        def handleCreateClick():
            index = self.listWidget_nas.currentRow()
            if index < 0:
                openMessageDialog("请选择要生成的外置路径")
                return
            obj = self.nasLink[index]
            print(obj)
            dir_path = os.path.join(obj["IP"], obj["dir"])
            if not os.path.exists(dir_path):
                openMessageDialog(f"找不到路径{dir_path}", "error")
                return
            print(dir_path)
            list_dir = os.listdir(dir_path)
            for dir_name in list_dir:
                GeneratedDirNas(dir_path, dir_name)
        self.btn_naslink_create.clicked.connect(handleCreateClick)

        def handleNasChange(event):
            self.btn_naslink_remove.setVisible(True)
        self.listWidget_nas.currentItemChanged.connect(handleNasChange) # 表格点击

    def get_nas_list(self): # nas列表数据加载
        if not self.listWidget_nas.count():
            for item in self.nasLink:
                self.listWidget_nas.addItem(f'{item["remark"]}{os.linesep}存储位置：{item["IP"]}  -  路径：{item["dir"]}')

    def initAuthorblock(self): # 阻止名单初始化
        self.virus = []

        # 黑名单列表点击
        def handleAuthorblockClick():
            obj = temp_authorblocklistnames[self.listWidget_authorblock.currentRow()]
            pyperclip.copy(f"名称: {obj['name']}{os.linesep}ID: {obj['value']}")
            openMessageDialog("已复制到剪贴板")
        self.listWidget_authorblock.itemClicked.connect(handleAuthorblockClick)

    def get_authorblock_list(self): # 阻止名单列表数据加载
        if len(temp_authorblocklistnames) != self.listWidget_authorblock.count():
            print('黑名单列表加载数据')
            for item in temp_authorblocklistnames:
                self.listWidget_authorblock.addItem(f"名称: {item['name']}{os.linesep}ID: {item['value']}")

    def initVirus(self): # 毒狗名单初始化
        def handleVirusLabelClick():
            pyperclip.copy("https://zhizhuzi.0d000721.cc/")
            openMessageDialog("网址已复制到剪贴板")
        self.btn_virus_label.clicked.connect(handleVirusLabelClick)
        # 毒狗列表点击
        def handleVirusClick():
            obj = self.virus[self.listWidget_virus.currentRow()]
            pyperclip.copy(f"名称: {obj['personaname']}{os.linesep}profileurl: {obj['profileurl']}")
            openMessageDialog("已复制到剪贴板")
        self.listWidget_virus.itemClicked.connect(handleVirusClick)
        # 域名生成steamworks key
        self.btn_virus_new.clicked.connect(lambda: openMessageDialog("404 域名没啦"))
        # 传入steamid列表 返回查询基本信息
        # https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/
        self.btn_virus_refresh.clicked.connect(lambda: openMessageDialog("steamworks key 失效"))
        
        try:
            path = os.path.join(os.getcwd(), 'virus')
            if os.path.exists(path):
                f1 = open(os.path.join(path, 'virus.json'), encoding="utf-8")
                self.virus = json.load(f1)
                f1.close()
        except Exception as e:
            logging.error(f"读取virus.json: {e}")
        
    def get_virus_list(self): # 毒狗名单列表数据加载
        if not self.listWidget_virus.count():
            print('毒狗列表加载数据')
            self.listWidget_virus.setIconSize(QSize(48, 48))
            for item in self.virus:
                strIsBlock = ""
                for obj in temp_authorblocklistnames:
                    if obj["value"] == item["steamid"]:
                        strIsBlock = "【已拉黑】"
                        break
                note = f'{item["steamid"]}{strIsBlock}{os.linesep}目前名字：{item["personaname"]}{os.linesep}{" // ".join(item["realname"])}'
                # print(os.path.join(os.getcwd(), 'virus', item["avatarmedium"]))
                icon = QPixmap(os.path.join(os.getcwd(), 'virus', item["avatarmedium"]))
                icon.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                item = QListWidgetItem(icon, note)
                self.listWidget_virus.addItem(item)

    def initTemp(self): # 临时文件夹初始化
        self.TempDir = config["TempDir"]
        def handleNewClick():
            path = openDirDialog()
            if path:
                self.TempDir.append(path)
                self.listWidget_temp.addItem(path)
        self.btn_temp_new.clicked.connect(handleNewClick)
        
        def handleRemoveClick():
            index = self.listWidget_temp.currentRow()
            if index >=0:
                del self.TempDir[index]
                self.listWidget_temp.takeItem(index)
                self.listWidget_temp.setCurrentRow(-1)
                self.btn_temp_remove.setVisible(False)
            else:
                openMessageDialog("请选择需要删除的地址！")
        self.btn_temp_remove.clicked.connect(handleRemoveClick)
        self.btn_temp_remove.setVisible(False)

        def handleTempChange(event):
            self.btn_temp_remove.setVisible(True)
        self.listWidget_temp.currentItemChanged.connect(handleTempChange) # 表格点击

    def get_temp_list(self): # 临时文件夹加载
        if not self.listWidget_temp.count():
            for item in self.TempDir:
                self.listWidget_temp.addItem(item)

    def resizeEvent(self, event): # 窗口变化
        if self.windowWidth == self.size().width():
            return
        self.windowDebouncer.trigger()


if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()
