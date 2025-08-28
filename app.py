from PySide6.QtWidgets import QApplication, QWidget
from widgets import Ui_MainForm, Ui_tableItemBox
from modules import MainFun, ConfigFun

class MyWindow(QWidget, Ui_MainForm):
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
            list = MainFun.get_data_list(mainConfig.config['backupPath']) # 获取列表数据
            self.set_list(list) 
            # mainConfig.get_wallpaper_config_path(wallpaper_path) # 获取wallpaper_config数据
        else:
            self.widget_1.hide()

    # 设置列表数据
    def set_list(self, list):
        # print(list)
        self.tableWidget_1.horizontalHeader().setStretchLastSection(True) # 表格自适应
        self.tableWidget_1.horizontalHeader().setVisible(False) # 隐藏头
        self.tableWidget_1.verticalHeader().setVisible(False) # 隐藏侧边
        self.tableWidget_1.setColumnCount(1)
        self.tableWidget_1.setRowCount(len(list))
        for index, item in enumerate(list):
            self.tableWidget_1.setRowHeight(index, 140)
            boxItem = Ui_tableItemBox()
            boxItem.retranslateUi(item['name'], item['path'])
            self.tableWidget_1.setCellWidget(index, 0, boxItem)


if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()