import os, logging, json, pyperclip
# PySide6组件调用
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QListWidgetItem
# 加载模板
from widgets import Ui_MainForm, Ui_List
# 功能模块
from modules.main import getDirList, openFileDialog, openStartfile, openMessageDialog, Unlock_hidden_achievements, Debouncer
from modules.Config import config, setSteamPath, setWallpaperPath, setBackupPath, set_config, save_config
from modules.RePKG import updataRepkg, processItem, updataRepkgData, setRepkgImgData
from modules.Mklink import mklinkCreate, mklinkNew, mklinkBack

class MyWindow(QWidget, Ui_MainForm):
    def __init__(self):
        self.wallpaperConfig = {}
        self.tabRepkgCurrent = False # 锁定tabRepkg页刷新
        self.tabMainError = True # 防止重复加载
        self.tabBackError = True # 防止重复加载

        super().__init__()
        self.initPage()
        self.initRepkg()
        self.initMklink()
        # self.initNaslink()

        # 加载数据
        self.tabChange()

    def func(self, *args, **kwargs):
        print(11112)
        pass

    # 初始化设置界面
    def initPage(self):
        self.setupUi(self)
        self.tabWidget.currentChanged.connect(self.tabChange)
        self.label_version.setText('版本：' + config["version"])
        self.btn_unlock_hidden_achievements.clicked.connect(Unlock_hidden_achievements)

        # 获取steam地址
        steam_path = config["steamPath"]
        self.lineEdit_steamPath.setText(steam_path)
        self.btn_steamPath.clicked.connect(lambda: setSteamPath(self.lineEdit_steamPath))
        # 获取wallpaper地址
        if config["wallpaperPath"]:
            self.lineEdit_wallpaperPath.setText(config["wallpaperPath"])
            self.btn_wallpaperPath.clicked.connect(lambda: setWallpaperPath(self.lineEdit_wallpaperPath))
            self.lineEdit_wallpaperBackupPath.setText(config["backupPath"])
            self.btn_wallpaperBackupPath.clicked.connect(lambda: setBackupPath(self.lineEdit_wallpaperBackupPath))
        # 黑名单列表点击
        self.listWidget_authorblock.itemClicked.connect(self.authorblockChange)


    # 窗口变化
    def resizeEvent(self, event):
        if self.tabRepkgCurrent:
            # print(f"窗口大小已更新为: {self.size().width()}x{self.size().height()}")
            self.debouncer.trigger()

    # tabWidget切换
    def tabChange(self):
        self.tabRepkgCurrent = False
        if self.tabWidget.currentIndex() == 0: # 壁纸加载
            if self.tabMainError: # 防止重复加载
                if config['mklinkList'][0]["path"]:
                    obj = Ui_List('main')
                    objChildren = self.tab_main.children()
                    objChildren[0].addWidget(obj)
                else:
                    self.addLabelError(self.tab_main)
                self.tabMainError = False
        elif self.tabWidget.currentIndex() == 1: # 备份壁纸加载
            if self.tabBackError: # 防止重复加载
                if config["backupPath"]:
                    obj2 = Ui_List('backup')
                    # 获取列表数据加载
                    # obj2.setData(getDirList(config["backupPath"]))
                    objChildren = self.tab_backup.children()
                    objChildren[0].addWidget(obj2)
                else:
                    self.addLabelError(self.tab_backup)
                self.tabBackError = False
        elif self.tabWidget.currentIndex() == 2: # repkg加载
            self.tabRepkgCurrent = True
            updataRepkg(config["repkgPath"], self.lineEdit_repkg, self.tableWidget_repkg)
        elif self.tabWidget.currentIndex() == 5: # 黑名单加载
            self.addauthorblockList()

    # 黑名单列表数据加载
    def addauthorblockList(self):
        print('黑名单加载')
        for item in config["authorblocklistnames"]:
            self.listWidget_authorblock.addItem(f"名称: {item['name']}\nID: {item['value']}")

    # 未安装Wallpaper Engine提示
    def addLabelError(self, tab):
        obj = QLabel('您未安装Wallpaper Engine')
        font = QFont()
        font.setPointSize(20)
        obj.setFont(font)
        obj.setLineWidth(1)
        obj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        objChildren = tab.children()
        objChildren[0].addWidget(obj)
   
    # repkg初始化
    def initRepkg(self):
        self.debouncer = Debouncer(lambda: setRepkgImgData(self.tableWidget_repkg, self.size().width()), 700)
        self.tableWidget_repkg.horizontalHeader().setStretchLastSection(True) # 表格自适应
        # self.tableWidget_repkg.horizontalHeader().setVisible(True) # 隐藏头
        # self.tableWidget_repkg.verticalHeader().setVisible(True) # 隐藏侧边
        self.repkgPath = config["repkgPath"]
        # repkg选择
        def __set_repkg_path():
            __path = openFileDialog(self.repkgPath, "请在场景壁纸中选择一个PKG/MPKG文件", "PKG/MPKG Files (*.pkg;*.mpkg)")
            if __path:
                self.repkgPath = __path
                self.lineEdit_repkg.setText(__path)
        self.btn_repkgPath.clicked.connect(__set_repkg_path)
        # repkg提取
        def __repkg_btn():
            res = processItem(self.repkgPath)
            # print(res)
            if res:
                set_config('repkgPath', self.repkgPath)
                # 写入config.json
                save_config()
                updataRepkgData()
                setRepkgImgData(self.tableWidget_repkg)
        self.btn_repkg.clicked.connect(__repkg_btn)

    # 软地址初始化
    def initMklink(self):
        self.mklinkCurrent = 1 # 当前启用的软地址
        self.updataMklink(self.mklinkCurrent)
        self.listWidget_mklink.itemClicked.connect(self.mklinkChange) # 表格点击
        self.btn_mklink_open_old.clicked.connect(lambda: openStartfile(self.lineEdit_mklink_path.text())) # mklink打开资源管理器
        self.btn_mklink_open.clicked.connect(lambda: openStartfile(self.lineEdit_mklink_path_new.text())) # mklink打开资源管理器
        # 新增
        def mklink_new():
            obj = mklinkNew()
            if obj:
                self.listWidget_mklink.addItem(f"标注:{obj['name']}\n{obj['path']}\n未生成")
        self.btn_mklink_new.clicked.connect(mklink_new)
        # 移除
        def mklink_remove():
            del config["mklinkList"][self.mklinkCurrent]
            self.listWidget_mklink.takeItem(self.mklinkCurrent)
            self.listWidget_mklink.setCurrentRow(1) # 选中
            self.mklinkChange() # 选中
            save_config()
        self.btn_mklink_remove.clicked.connect(mklink_remove)
        # 生成软链接
        def mklink_create():
            dir_path_new = mklinkCreate(self.mklinkCurrent)
            if dir_path_new:
                data = config["mklinkList"]
                data[self.mklinkCurrent]['path_new'] = dir_path_new
                # 写入config.json
                save_config()
                self.listWidget_mklink.currentItem().setText(f"标注:{data[self.mklinkCurrent]['name']}\n{data[self.mklinkCurrent]['path']}\n{data[self.mklinkCurrent]['path_new'] or '未生成'}")
                self.lineEdit_mklink_path_new.setText(data[self.mklinkCurrent]['path_new'])
        self.btn_mklink_create.clicked.connect(mklink_create)
        # 还原
        def mklink_back():
            if mklinkBack(self.mklinkCurrent):
                data = config["mklinkList"]
                data[self.mklinkCurrent]['path_new'] = ""
                save_config()
                self.listWidget_mklink.currentItem().setText(f"标注:{data[self.mklinkCurrent]['name']}\n{data[self.mklinkCurrent]['path']}\n未生成")
                self.lineEdit_mklink_path_new.setText("")
        self.btn_mklink_restore.clicked.connect(mklink_back)

    # Mklink列表加载数据
    def updataMklink(self, current = 1):
        mklinkList = config["mklinkList"]
        for index, item in enumerate(mklinkList):
            self.listWidget_mklink.addItem(f"标注:{item['name']}\n{item['path']}\n{item['path_new'] or '未生成'}")
        self.listWidget_mklink.setCurrentRow(current) # 选中
        self.mklinkChange() # 选中

    # 软地址切换
    def mklinkChange(self, item = None):
        # print(f"Item clicked: {item.text()} at ({self.listWidget_mklink.currentRow()})")
        self.mklinkCurrent = self.listWidget_mklink.currentRow()
        obj = config["mklinkList"][self.mklinkCurrent]
        self.lineEdit_mklink_path.setText(obj['path'])
        self.lineEdit_mklink_path_new.setText(obj['path_new'])
        self.btn_mklink_remove.setVisible(self.mklinkCurrent > 1)
    
    # 黑名单列表点击
    def authorblockChange(self):
        authorblockCurrent = self.listWidget_authorblock.currentRow()
        obj = config["authorblocklistnames"][authorblockCurrent]
        openMessageDialog("已复制到剪贴板")
        pyperclip.copy(f"名称: {obj['name']}\nID: {obj['value']}")


if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()
