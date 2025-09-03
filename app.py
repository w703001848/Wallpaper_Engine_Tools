import os, logging
# PySide6组件调用
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QWidget, QLabel
# 加载模板
from widgets import Ui_MainForm, Ui_List
# 功能模块
from modules.main import getDirList, openFileDialog, openStartfile, Debouncer
from modules.Config import config, setSteamPath, setWallpaperPath, setBackupPath, set_config, save_config
from modules.RePKG import updataRepkg, processItem, updataRepkgData, setRepkgImgData
from modules.Mklink import mklinkCreate, mklinkNew, mklinkBack

class MyWindow(QWidget, Ui_MainForm):
    def __init__(self):
        self.wallpaperConfig = {}

        super().__init__()
        self.initPage()
        self.initRepkg()
        self.initMklink()

    def func(self, *args, **kwargs):
        print(11112)
        pass

    # 初始化设置界面
    def initPage(self):
        self.setupUi(self)
        self.tabWidget.currentChanged.connect(self.tabChange)
        self.label_version.setText('版本：' + config["version"])

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
            
            # self.get_wallpaper_config_path(wallpaper_path) # 获取wallpaper_config数据
            self.addMainList() 
        else:
            self.addLabelError()

    def resizeEvent(self, event):
        if self.tabCurrent:
            # print(f"窗口大小已更新为: {self.size().width()}x{self.size().height()}")
            self.debouncer.trigger()

    # tabWidget切换
    def tabChange(self):
        if self.tabWidget.currentIndex() == 2:
            self.tabCurrent = True
            updataRepkg(config["repkgPath"], self.lineEdit_repkg, self.tableWidget_repkg)
        else:
            self.tabCurrent = False

    # 列表数据加载
    def addMainList(self):
        obj = Ui_List('main')
        objChildren = self.tab_main.children()
        objChildren[0].addWidget(obj)

        obj2 = Ui_List('backup')
        # 获取列表数据加载
        obj2.setData(getDirList(config["backupPath"]))
        objChildren = self.tab_backup.children()
        objChildren[0].addWidget(obj2)

    # 未安装Wallpaper Engine提示
    def addLabelError(self):
        obj = QLabel('您未安装Wallpaper Engine', self)
        font = QFont()
        font.setPointSize(20)
        obj.setFont(font)
        obj.setLineWidth(1)
        obj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        objChildren = self.tab_main.children()
        objChildren[0].addWidget(obj)
   
    # repkg初始化
    def initRepkg(self):
        self.tabCurrent = False
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
        self.listWidget_mklink.itemClicked.connect(self.listWidgetChange) # 表格点击
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
            self.listWidgetChange() # 选中
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
        self.listWidgetChange() # 选中

    # 软地址切换
    def listWidgetChange(self, item = None):
        # print(f"Item clicked: {item.text()} at ({self.listWidget_mklink.currentRow()})")
        self.mklinkCurrent = self.listWidget_mklink.currentRow()
        obj = config["mklinkList"][self.mklinkCurrent]
        self.lineEdit_mklink_path.setText(obj['path'])
        self.lineEdit_mklink_path_new.setText(obj['path_new'])
        self.btn_mklink_remove.setVisible(self.mklinkCurrent > 1)

    # 获取WallpaperEngine config位置并读取
    # def get_wallpaper_config_path(self, wallpaper_path): 
    #     wallpaper_config_path = os.path.join(wallpaper_path, 'config.json')
    #     try:
    #         with open(wallpaper_config_path, encoding="utf-8") as f1:
    #             res = json.load(f1) # 从文件读取json并反序列化
    #             print(res)
    #     except Exception as e:
    #         logging.error(f"获取WallpaperEngine config位置并读取: {e}")

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()
