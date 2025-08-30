import os, logging

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QRadioButton
from widgets import Ui_MainForm
from modules import MainFun, ConfigFun, Ui_List, RePKGFun

class MyWindow(QWidget, Ui_MainForm):
    def __init__(self):
        self.configFun = ConfigFun()
        self.wallpaperConfig = {}

        super().__init__()
        self.initPage()

    # 初始化设置界面
    def initPage(self):
        self.setupUi(self)

        self.label_version.setText('版本：' + self.configFun.config['version'])
        # 获取steam地址
        steam_path = self.configFun.config['steamPath']
        self.lineEdit_steamPath.setText(steam_path)
        self.btn_steamPath.clicked.connect(self.setSteamPath)
        # 获取wallpaper地址
        if self.configFun.config['wallpaperPath']:
            self.lineEdit_wallpaperPath.setText(self.configFun.config['wallpaperPath'])
            self.btn_wallpaperPath.clicked.connect(self.setWallpaperPath)
            self.lineEdit_wallpaperBackupPath.setText(self.configFun.config['backupPath'])
            self.btn_wallpaperBackupPath.clicked.connect(self.setBackupPath)
            
            # self.configFun.get_wallpaper_config_path(wallpaper_path) # 获取wallpaper_config数据
            self.addMainList() 
        else:
            self.addLabelError()
        
        self.repkgInit()
        self.mklinkInit()

    def func(self, *args, **kwargs):
        print(11112)
        pass
    
    # 设置文本框steam地址
    def setSteamPath(self):
        # path = MainFun.openFileDialog(self.configFun.config['steamPath'])
        path = MainFun.openFileDialog(self.configFun.config['steamPath'], "请选择steam.exe启动文件", "Steam (*.exe)")
        if path:
            self.configFun.set_steam_path(path)
            self.lineEdit_steamPath.setText(path)
            self.mklinkChange(self.radio_mklink_steam) # 选中
            # self.radio_mklink_steam.setChecked(True) 无法给文本框赋值
            # 写入config.json
            self.configFun.save_config()

    # 设置文本框wallpaper地址
    def setWallpaperPath(self):
        # path = MainFun.openDirDialog(self.configFun.config['wallpaperPath'])
        path = MainFun.openFileDialog(self.configFun.config['wallpaperPath'], "请选择wallpaper_engine/launcher.exe启动文件", "Steam (*.exe)")
        if path:
            self.lineEdit_wallpaperPath.setText(path)
            self.configFun.set_wallpaper_path(path)
            # 写入config.json
            self.configFun.save_config()

    # 设置文本框backup地址
    def setBackupPath(self):
        path = MainFun.openDirDialog(self.configFun.config['backupPath'])
        if path:
            self.lineEdit_wallpaperBackupPath.setText(path)
            self.configFun.set_wallpaper_backup_path(path)
            self.mklinkChange(self.radio_mklink_backup) # 选中
            # 写入config.json
            self.configFun.save_config()

    # 列表数据加载
    def addMainList(self):
        obj = Ui_List('main')
        objChildren = self.tab_main.children()
        objChildren[0].addWidget(obj)

        obj2 = Ui_List('backup')
        # 获取列表数据加载
        obj2.setData(MainFun.getDirList(self.configFun.config['backupPath']))
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
        self.gridLayout_tabMain.addWidget(obj)
   
    # repkg初始化
    def repkgInit(self):
        self.tabWidget.currentChanged.connect(self.repkgChange)
        self.btn_repkg.clicked.connect(self.repkgBtn)

        def func():
            path = MainFun.openFileDialog(self.configFun.config['repkgPath'], "请在场景壁纸中选择一个PKG/MPKG文件", "PKG/MPKG Files (*.pkg;*.mpkg)")
            if path:
                self.configFun.set_config('repkgPath', path)
                self.lineEdit_repkg.setText(path)
                # 写入config.json
                # self.configFun.save_config()
        self.btn_repkgPath.clicked.connect(func)

    # repkg生成数据加载
    def repkgChange(self):
        if self.tabWidget.currentIndex() == 2:
            # print(RePKGFun().steamDirs)
            # print(self.configFun.config['repkgPath'])
            if RePKGFun().steamDirs != '' and RePKGFun().steamDirs != self.configFun.config['repkgPath']:
                path = RePKGFun().steamDirs
                self.configFun.set_config('repkgPath', path)
                self.lineEdit_repkg.setText(path)
                self.setRepkgImgData()

    # repkg提取
    def repkgBtn(self):
        res = RePKGFun().processItem(self.configFun.config['repkgPath'])
        # print(res)
        if res:
            self.setRepkgImgData()

    # repkg图表生成
    def setRepkgImgData(self):
        dirPath = os.path.join(os.getcwd(), RePKGFun().output)
        if not os.path.exists(dirPath):
            return
        data = os.listdir(dirPath)
        self.tableWidget_repkg.horizontalHeader().setStretchLastSection(True) # 表格自适应
        # self.tableWidget_repkg.horizontalHeader().setVisible(False) # 隐藏头
        # self.tableWidget_repkg.verticalHeader().setVisible(False) # 隐藏侧边
        colMax = 3
        self.tableWidget_repkg.setColumnCount(colMax)
        self.tableWidget_repkg.setRowCount(int(len(data) / colMax + 0.5))
        size = 199
        row = 0
        col = 0
        self.tableWidget_repkg.setColumnWidth(0, size)
        self.tableWidget_repkg.setColumnWidth(1, size)
        self.tableWidget_repkg.setColumnWidth(2, size)
        self.tableWidget_repkg.setRowHeight(0, size)
        for index, item in enumerate(data):
            imgPath = os.path.join(dirPath, item)
            boxItem = QLabel()
            boxItem.setMinimumSize(QSize(size, size))
            boxItem.setMaximumSize(QSize(size, size))
            boxItem.setScaledContents(True)
            boxItem.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pic = QPixmap(imgPath)
            boxItem.setPixmap(pic)
            self.tableWidget_repkg.setCellWidget(row, col, boxItem)
            col += 1
            if col >= colMax:
                col = 0
                row += 1
                self.tableWidget_repkg.setRowHeight(row, size)

    # 软地址初始化
    def mklinkInit(self):
        self.radio_mklink_steam.index = 0
        self.radio_mklink_backup.index = 1
        self.mklinkChange(self.radio_mklink_backup) # 初始化选中
        self.buttonGroup.buttonClicked.connect(self.mklinkChange)
        self.btn_mklink_open_old.clicked.connect(lambda: MainFun.openStartfile(self.lineEdit_mklink_path.text())) # mklink打开资源管理器
        self.btn_mklink_open.clicked.connect(lambda: MainFun.openStartfile(self.lineEdit_mklink_path_new.text())) # mklink打开资源管理器
        self.btn_mklink_create.clicked.connect(lambda: self.mklinkBtn())
        self.btn_mklink_restore.clicked.connect(lambda: self.configFun.backMklink()) # 还原
        self.btn_mklink_new.clicked.connect(self.mklinkNew) # 新增
            # # 获取wallpaper软链接地址
            # if self.configFun.config['mklinkWallpaperOld'] and self.configFun.config['mklinkWallpaper'] != self.configFun.config['mklinkWallpaperOld']:
            #     self.lineEdit_mklink_path.setText(self.configFun.config['mklinkWallpaperOld'])
            #     self.lineEdit_mklink_path_new.setText(self.configFun.config['mklinkWallpaper'])
        
    # 软地址生成
    def mklinkBtn(self):
        index = self.configFun.config['mklinkIndex']
        if index < 0:
            return
        res = MainFun.openMessageDialog("生成前请先备份!确认后选择空文件夹开始执行。")
        if res:
            # print("用户点击了确定")
            dir_path = self.lineEdit_mklink_path.text()
            MainFun.openStartfile(os.path.dirname(dir_path))
            dir_path_new = MainFun.openDirDialog(dir_path)
            if dir_path_new: 
                isSuccess = MainFun.create_symbolic_link(dir_path, dir_path_new)
                if isSuccess:
                    print(555)
                    self.lineEdit_mklink_path_new.setText(dir_path_new)
                    data = self.configFun.config['mklinkList']
                    data[index]['path'] = dir_path
                    data[index]['path_new'] = dir_path_new
                    # 写入config.json
                    self.configFun.save_config()

    # 软地址切换
    def mklinkChange(self, radioBtn:QRadioButton):
        # print(radioBtn.text())
        self.configFun.set_config('mklinkIndex', radioBtn.index)
        obj = self.configFun.config['mklinkList'][radioBtn.index]
        self.lineEdit_mklink_path.setText(obj['path'])
        self.lineEdit_mklink_path_new.setText(obj['path_new'])

    # 软地址新增
    def mklinkNew(self, index, path, path_new):
        mklinkList = self.configFun.config['mklinkList']
        name = f"额外{index}"
        mklinkList.append({
            "name": name,
            "path": path,
            "path_new": path_new
        })
        self.configFun.save_config()
        self.mklinkBtnNew(index, name)

    # 软地址按钮新增
    def mklinkBtnNew(self, index, name):
        btn = QRadioButton()
        btn.index = index
        btn.objectName = f"radio_mklink_{index}"
        btn.setText(name)
        self.buttonGroup.addButton(btn)
        self.horizontalLayout_radio.addWidget(btn)
        btn.setChecked(True)

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()