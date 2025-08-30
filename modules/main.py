import logging  # 引入logging模块
import os
import json
import winreg as reg
import shutil
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget


class ConfigFun(object):
    config_path = os.path.join(os.getcwd(), 'config.json')

    def __init__(self):
        # 首次执行初始化config
        self.boolSetConfig = False
        self.config = {
            "isDevelopment": MainFun.checkEnvironment(),
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
            "mklinkIndex": -1, # 当前启用的软地址
            "mklinkList": [],
            "repkgPath": "", # RePKG
            "isCheckedRePKGClear": False, # 是否清空RePKG上次输出
        }
        
        # 查询是否存在并获取config.json
        if os.path.exists(ConfigFun.config_path):
        # if self.config['isDevelopment'] and os.path.exists(ConfigFun.config_path):
            self.get_config()

        if not self.config['steamPath']:
            path = self.get_steam_path_registry()
            self.boolSetConfig = self.set_steam_path(os.path.abspath(path+'/steam.exe'), True)
        if not self.config['wallpaperPath']:
            path = self.get_wallpaper_path_registry()
            self.boolSetConfig = self.set_wallpaper_path(os.path.abspath(path+'/launcher.exe'))
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

    # 获取WallpaperEngine config位置并读取
    def get_wallpaper_config_path(self, wallpaper_path): 
        wallpaper_config_path = os.path.join(wallpaper_path, 'config.json')
        try:
            with open(wallpaper_config_path, encoding="utf-8") as f1:
                res = json.load(f1) # 从文件读取json并反序列化
                print(res)
        except Exception as e:
            logging.error(f"获取WallpaperEngine config位置并读取: {e}")

    # 注册表获取Steam安装位置
    def get_steam_path_registry(self): 
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

    # 注册表获取WallpaperEngine安装位置
    def get_wallpaper_path_registry(self): 
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
        try:
            path_dir = os.path.join(os.path.dirname(self.config['wallpaperPath']), 'projects\\backup')
            if os.path.exists(path_dir):
                return path_dir
            else:
                return ''
        except Exception as e:
            logging.error(f"获取WallpaperEngine备份位置: {e}")
            return None
    
    # 修改Steam安装位置
    def set_steam_path(self, path, isFirst=False):
        if path:
            self.set_config('steamPath', path)
            # 是否首次获取并自动配置软链接
            if isFirst:
                self.config['mklinkList'].append({
                    "name": "订阅",
                    "path": self.get_mklink_steam_path(),
                    "path_old": ""
                })
            else:
                data = self.config['mklinkList']
                for i in data:
                    if i['name'] == "订阅":
                        i['path'] = self.get_mklink_steam_path()
                        break
        return True

    # 修改WallpaperEngine安装位置
    def set_wallpaper_path(self, path):
        if path:
            self.set_config('wallpaperPath', path)
            if not self.config['backupPath']:
                self.set_wallpaper_backup_path(self.get_wallpaper_backup_path(), True)
        return True

    # 修改WallpaperEngine备份位置
    def set_wallpaper_backup_path(self, path, isFirst=False):
        if path:
            self.set_config('backupPath', path)
            # 是否首次获取并自动配置软链接
            if isFirst:
                self.config['mklinkList'].append({
                    "name": "备份",
                    "path": path,
                    "path_old": ""
                })
            else:
                data = self.config['mklinkList']
                for i in data:
                    if i['name'] == "备份":
                        i['path'] = path
                        break

    # 获取Steam软链接地址
    def get_mklink_steam_path(self): 
        try:
            path = os.path.join(os.path.dirname(self.config['steamPath']), 'steamapps\\workshop\\content\\431960')
            if os.path.exists(path):
                return path
            else:
                MainFun.openMessageDialog('当前steam文件夹下无法查询到壁纸订阅目录!')
                raise Exception("当前steam文件夹下无法查询到壁纸订阅目录!", path)
        except Exception as e:
            logging.error(f"获取Steam软链接地址: {e}")
            return None
        
    # # 获取WallpaperEngine软链接地址
    # def get_mklink_wallpaper_path(self): 
    #     try:
    #         path = self.config['backupPath']
    #         if os.path.exists(path):
    #             return path
    #         else:
    #             return ''
    #     except Exception as e:
    #         logging.error(f"获取WallpaperEngine软链接地址: {e}")
    #         return None

    # 软链接选择
    def openMklinkDialog(self, path, boxText: QWidget):
        def func():
            # print("用户点击了确定")
            dir_path = MainFun.openDirDialog(path, func)
            if dir_path: 
                boxText.setText(dir_path)
                self.create_symbolic_link(path)
        MainFun.openMessageDialog("生成前请先备份!确认后选择空文件夹开始执行。", func)
    
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
    def backMklink(self):
        pass
            

# print(PYTHON_ENV)
# obj = ConfigFun()



class MainFun(object):

    # 用于传参，默认函数
    def func(*args, **kwargs):
        pass

    # 警告弹窗
    def openMessageDialog(txt="警告", funOK=func, funCancel=func):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)  # 设置图标为警告
        msg.setText(txt)  # 设置消息文本
        msg.setWindowTitle("警告")  # 设置窗口标题
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  # 设置按钮
        # 执行模态对话框，返回点击的按钮
        ret = msg.exec()
        if ret == QMessageBox.Ok:
            funOK(ret)
        elif ret == QMessageBox.Cancel:
            funCancel(ret)

    # 打开资源管理器
    def openStartfile(path):
        try:
            if path == '':
                raise Exception("空参数值!")
            os.startfile(path)
        except Exception as e:
            logging.error(e)   

    # 选择一个文件
    def openFileDialog(path=None, title="选择一个文件", type="All Files (*)", funOK=func, funCancel=func): # Text Files (*.txt);;All Files (*)
        file_name, _ = QFileDialog.getOpenFileName(None, title, path, type)
        if file_name:
            funOK(file_name)
            return file_name
        else:
            funCancel()
            return False
        
    # 选择一个文件夹
    def openDirDialog(path=None, title ="选择一个文件夹", funOK=func, funCancel=func): 
        dir_path = QFileDialog.getExistingDirectory(None, title, path)
        if dir_path:
            funOK(dir_path)
            return dir_path
        else:
            funCancel()
            return False
        
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

    # 是否正式版
    def checkEnvironment():
        PYTHON_ENV = os.path.exists(os.path.join(os.getcwd(), 'app.py'))
        if PYTHON_ENV:
            # development
            print("开发环境")
            return False
        else:
            print("正式环境")
            return True

