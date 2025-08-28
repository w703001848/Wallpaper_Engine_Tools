from PySide6.QtWidgets import QApplication, QWidget, QFileDialog
from widgets import UI_MainForm
from modules import MainFun, ConfigFun
import os
class MyWindow(QWidget, UI_MainForm):
    def __init__(self):
        self.config = {
            "version": "1.1"
        }
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setupUi(self)
        mainConfig = ConfigFun()
        self.label_version.setText('版本：' + self.config['version'])
        # 获取steam数据
        steam_path = mainConfig.config['steamPath']
        self.lineEdit_steamPath.setText(steam_path)
        self.btn_steamPath.clicked.connect(lambda: mainConfig.openFileDialog('steamPath', self.lineEdit_steamPath))
        # 获取wallpaper数据
        if mainConfig.config['wallpaperPath']:
            # print("wallpaper path:", mainConfig.config['wallpaperPath'])
            self.lineEdit_wallpaperPath.setText(mainConfig.config['wallpaperPath'])
            self.btn_wallpaperPath.clicked.connect(lambda: mainConfig.openFileDialog('wallpaperPath', self.lineEdit_wallpaperPath))
            self.lineEdit_wallpaperBackupPath.setText(mainConfig.config['backupPath'])
            self.btn_wallpaperBackupPath.clicked.connect(lambda: mainConfig.openFileDialog('backupPath', self.lineEdit_wallpaperBackupPath))
            self.label_error.hide()
        else:
            self.scrollArea.hide()
            # mainConfig.get_wallpaper_config_path(wallpaper_path)
        

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()