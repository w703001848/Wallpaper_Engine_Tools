import logging  # 引入logging模块
import os
import json
import winreg as reg
import shutil
from PySide6.QtWidgets import QFileDialog, QMessageBox


class ConfigFun(object):
    config_path = os.path.join(os.getcwd(), 'config.json')

    def __init__(self):
        # 首次执行初始化config
        self.boolSetConfig = False
        self.config = {
            "version": "1.1",
            "username": os.getlogin(), # 获取本机用户名
            "isCheckedScene": True, # 场景
            "isCheckedVideo": False, # 视频
            "isCheckedWeb": False, # 网页
            "isCheckedApplication": False, # 应用
            "isCheckedInvalid": False, # 失效
            "steamPath": "", # steam地址
            "wallpaperPath": "", # wallpaper地址
            "backupPath": "", # wallpaper备份地址
            "mklinkSteam": "",
            "mklinkWallpaper": "",
            "mklinkSteamOld": "",
            "mklinkWallpaperOld": "",
            "radioMklink": 0,
            "repkgPath": "", # RePKG
            "isCheckedRePKGClear": False, # 是否清空RePKG上次输出
        }
        
        # 获取config.json
        if os.path.exists(ConfigFun.config_path):
            self.get_config()
        if not self.config['steamPath']:
            self.set_config('steamPath', self.get_steam_path())
        if not self.config['wallpaperPath']:
            self.set_config('wallpaperPath', self.get_wallpaper_path())
        if not self.config['backupPath']:
            self.set_config('backupPath', self.get_wallpaper_backup_path())
        # if not self.config['mklinkSteam']:
        #     self.set_config('mklinkSteam', self.get_mklink_steam_path())
        # if not self.config['mklinkWallpaper']:
        #     self.set_config('mklinkWallpaper', self.get_mklink_wallpaper_path())
        # if not self.config['mklinkSteamOld']:
        #     self.set_config('mklinkSteamOld', self.config['mklinkSteam'])
        # if not self.config['mklinkWallpaperOld']:
        #     self.set_config('mklinkWallpaperOld', self.config['mklinkWallpaper'])
        if self.boolSetConfig:
            # 写入config.json
            self.save_config()

    # 读取config.json
    def get_config(self): 
        try:
            with open(self.config_path, encoding="utf-8") as f1:
                self.config = json.load(f1) # 从文件读取json并反序列化
        except Exception as e:
            logging.warning(f"读取config.json: {e}")

    # 设置config.json
    def set_config(self, key, obj): 
        try:
            if self.config[key] != obj:
                self.config[key] = obj
                self.boolSetConfig = True
        except Exception as e:
            logging.warning(f"设置config.json: {e}")

    # 写入config.json
    def save_config(self): 
        try:
            with open(self.config_path, mode='wt', encoding="utf-8") as f1:
                json.dump(self.config, f1) # 将json写入文件
                self.boolSetConfig = False
        except Exception as e:
            logging.warning(f"写入config.json: {e}")

    # 警告弹窗
    def openMessageDialog(self, txt, funOK, funCancel):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)  # 设置图标为警告
        msg.setText(txt)  # 设置消息文本
        msg.setWindowTitle("警告")  # 设置窗口标题
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  # 设置按钮
        # 执行模态对话框，返回点击的按钮
        ret = msg.exec()
        if ret == QMessageBox.Ok:
            funOK()
        elif ret == QMessageBox.Cancel:
            funCancel()
            
    # 选择一个文件
    def openFileDialog(self, path, boxText, type="All Files (*)"): # Text Files (*.txt);;All Files (*)
        file_name, _ = QFileDialog.getOpenFileName(None, "选择一个文件", self.config[path], type)
        if file_name:
            self.set_config(path, file_name)
            boxText.setText(file_name)
            # 写入config.json
            # self.save_config()
            return True
        else:
            return False
        
    # 选择一个文件夹
    def openDirDialog(self, path, boxText): 
        dir_path = QFileDialog.getExistingDirectory(None, "选择一个文件夹", self.config[path])
        if dir_path:
            self.set_config(path, dir_path)
            boxText.setText(dir_path)
            # 写入config.json
            self.save_config()
            return True
        else:
            return False

    # 获取WallpaperEngine config位置并读取
    def get_wallpaper_config_path(self, wallpaper_path): 
        wallpaper_config_path = os.path.join(wallpaper_path, 'config.json')
        try:
            with open(wallpaper_config_path, encoding="utf-8") as f1:
                res = json.load(f1) # 从文件读取json并反序列化
                print(res)
        except Exception as e:
            logging.error(f"获取WallpaperEngine config位置并读取: {e}")

    # 获取Steam安装位置
    def get_steam_path(self): 
        try:
            aReg = reg.ConnectRegistry(None, reg.HKEY_CURRENT_USER)
            aKey = reg.OpenKey(aReg, r"Software\Valve\Steam")
            path = reg.QueryValueEx(aKey, "SteamPath")[0]
            reg.CloseKey(aKey)
            if os.path.exists(path):
                return path
            else:
                return ''
        except Exception as e:
            logging.error(f"获取Steam安装位置: {e}")
            return None

    # 获取WallpaperEngine安装位置
    def get_wallpaper_path(self): 
        try:
            aReg = reg.ConnectRegistry(None, reg.HKEY_CURRENT_USER)
            aKey = reg.OpenKey(aReg, r"Software\WallpaperEngine")
            path = reg.QueryValueEx(aKey, "installPath")[0]
            reg.CloseKey(aKey)
            path_dir = os.path.dirname(path)
            if os.path.exists(path_dir):
                return path_dir
            else:
                return ''
        except Exception as e:
            logging.error(f"获取WallpaperEngine安装位置: {e}")
            return None
        
    # 获取WallpaperEngine备份位置
    def get_wallpaper_backup_path(self): 
        backupPath = os.path.join(self.config['wallpaperPath'], 'projects\\backup')
        return backupPath
    
    # 获取Steam软链接地址
    def get_mklink_steam_path(self): 
        try:
            path = os.path.join(self.config['steamPath'], 'steamapps\\workshop\\content\\431960')
            if os.path.exists(path):
                return path
            else:
                return ''
        except Exception as e:
            logging.error(f"获取Steam软链接地址: {e}")
            return None
        
    # 获取WallpaperEngine软链接地址
    def get_mklink_wallpaper_path(self): 
        try:
            path = self.config['backupPath']
            if os.path.exists(path):
                return path
            else:
                return ''
        except Exception as e:
            logging.error(f"获取WallpaperEngine软链接地址: {e}")
            return None

    # 软链接选择
    def openMklinkDialog(self, path, boxText):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)  # 设置图标为警告
        msg.setText("生成前请先备份!确认后选择空文件夹开始执行。")  # 设置消息文本
        msg.setWindowTitle("警告")  # 设置窗口标题
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  # 设置按钮
        # 执行模态对话框，返回点击的按钮
        ret = msg.exec()
        if ret == QMessageBox.Ok:
            # print("用户点击了确定")
            isBool = self.openDirDialog(path, boxText)
            if isBool: 
                self.create_symbolic_link(path)
            # print(self.config[path])
    
    # 软链接生成
    def create_symbolic_link(self, path):
        print(self.config[path])
        pathOld = path + 'Old'
        print(self.config[pathOld])
        # 重命名原目录
        pathOldBack = self.config[pathOld]+'_back'
        os.rename(self.config[pathOld], pathOldBack)
        try:
            if os.path.exists(self.config[pathOld]):
                shutil.rmtree(self.config[pathOld])
            os.symlink(self.config[path], self.config[pathOld])
            print(f"成功创建符号链接：{self.config[pathOld]} -> {self.config[path]}")
        except Exception as e:
            print(f"创建符号链接失败:{e}")
            # 回退
            os.rename(pathOldBack, self.config[pathOld])
            self.config[path] = self.config[pathOld]
            # 写入config.json
            self.save_config()
            raise

    # 回退
    def backMklink(self, path, boxText):
        pass



# obj = ConfigFun()



class MainFun(object):
    # 获取文件夹内项目列表
    def getDirList(path, isSize=False):
        list = []
        for item in os.listdir(path):
            obj = {
                "name": item,
                "path": os.path.join(path, item) # 结合目录名与文件名
            }
            obj['size'] = MainFun.getDirSize(obj['path']) if isSize else 0
            list.append(obj)
            
        return list
    
    # 文件夹容量计算
    def getDirSize(folder_path):
        logging.warning('开启文件夹容量计算，占用性能建议关闭')
        total_size = 0
        with os.scandir(folder_path) as entries:
            for entry in entries:
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += MainFun.getDirSize(entry.path)
        return total_size