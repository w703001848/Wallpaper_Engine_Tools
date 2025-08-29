import os, logging

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QLabel
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
        self.btn_steamPath.clicked.connect(lambda: self.configFun.openDirDialog('steamPath', self.lineEdit_steamPath))
        # 获取steam软连接地址
        # if self.configFun.config['mklinkSteamOld'] and self.configFun.config['mklinkSteam'] != self.configFun.config['mklinkSteamOld']:
        #     self.lineEdit_steamPath_mklink.setText(self.configFun.config['mklinkSteam'])
        # self.btn_steam_mklink.clicked.connect(lambda: self.configFun.openMklinkDialog('mklinkSteam', self.lineEdit_wallpaperBackupPath_mklink))
        # 获取wallpaper地址
        if self.configFun.config['wallpaperPath']:
            self.lineEdit_wallpaperPath.setText(self.configFun.config['wallpaperPath'])
            self.btn_wallpaperPath.clicked.connect(lambda: self.configFun.openDirDialog('wallpaperPath', self.lineEdit_wallpaperPath))
            self.lineEdit_wallpaperBackupPath.setText(self.configFun.config['backupPath'])
            self.btn_wallpaperBackupPath.clicked.connect(lambda: self.configFun.openDirDialog('backupPath', self.lineEdit_wallpaperBackupPath))
            # # 获取wallpaper软链接地址
            # if self.configFun.config['mklinkWallpaperOld'] and self.configFun.config['mklinkWallpaper'] != self.configFun.config['mklinkWallpaperOld']:
            #     self.lineEdit_wallpaperBackupPath_mklink.setText(self.configFun.config['mklinkWallpaper'])
            #     self.btn_backup_mklink.setText("还原")
            #     self.btn_backup_mklink.clicked.connect(lambda: self.configFun.backMklink('mklinkWallpaper', self.lineEdit_wallpaperBackupPath_mklink))
            # else:
            #     self.btn_backup_mklink.clicked.connect(lambda: self.configFun.openMklinkDialog('mklinkWallpaper', self.lineEdit_wallpaperBackupPath_mklink))

            # self.configFun.get_wallpaper_config_path(wallpaper_path) # 获取wallpaper_config数据
            self.addMainList() 
        else:
            self.addLabelError()

        self.tabWidget.currentChanged.connect(lambda: self.repkgInit())
        self.btn_repkgPath.clicked.connect(lambda: self.configFun.openFileDialog('repkgPath', self.lineEdit_repkg, "PKG/MPKG Files (*.pkg;*.mpkg)"))
        self.btn_repkg.clicked.connect(lambda: self.repkgBtn())
        
    def repkgInit(self):
        if self.tabWidget.currentIndex() == 2:
            if RePKGFun().steamDirs != '' and RePKGFun().steamDirs != self.configFun.config['repkgPath']:
                path = RePKGFun().steamDirs
                self.configFun.set_config('repkgPath', path)
                self.lineEdit_repkg.setText(path)
                self.setRepkgImgData()

    def repkgBtn(self):
        res = RePKGFun().processItem(self.configFun.config['repkgPath'])
        print(res)
        if res:
            self.setRepkgImgData()

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

    def xxx(self):
        pass

    def addMainList(self):
        obj = Ui_List('main')
        self.gridLayout_tabMain.addWidget(obj)

        obj2 = Ui_List('backup')
        # 获取列表数据加载
        obj2.setData(MainFun.getDirList(self.configFun.config['backupPath']))
        self.gridLayout_tabBackup.addWidget(obj2)

    def addLabelError(self):
        obj = QLabel('您未安装Wallpaper Engine', self)
        font = QFont()
        font.setPointSize(20)
        obj.setFont(font)
        obj.setLineWidth(1)
        obj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout_tabMain.addWidget(obj)


if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()