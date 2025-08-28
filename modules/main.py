import logging  # 引入logging模块
import os
import json
import winreg as reg
from PySide6.QtWidgets import QFileDialog

class MainFun(object):
     
    def get_data_list(path):
        list = []
        for item in os.listdir(path):
            obj = {
                "name": item,
                "path": os.path.join(path, item) # 结合目录名与文件名
            }
            list.append(obj)
            # print(list)
        return list


class ConfigFun(object):
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        # 首次执行初始化config
        self.config = {
            "username": os.getlogin(), # 获取本机用户名
            "steamPath": "", # steam地址
            "wallpaperPath": "", # wallpaper地址
            "backupPath": "", # wallpaper备份地址
            "isCheckedScene": True, # 场景
            "isCheckedVideo": False, # 视频
            "isCheckedWeb": False, # 网页
            "isCheckedApplication": False, # 应用
            "isCheckedInvalid": False, # 失效
        }
        
        # 获取config.json
        try:
            with open(self.config_path, encoding="utf-8") as f1:
                self.config = json.load(f1) # 从文件读取json并反序列化
        except Exception as e:
            logging.warning(f"Warning accessing registry: {e}")
        if not self.config['steamPath']:
            self.config['steamPath'] = self.get_steam_path()
        if not self.config['wallpaperPath']:
            self.config['wallpaperPath'] = self.get_wallpaper_path()
        if not self.config['backupPath']:
            self.config['backupPath'] = self.get_wallpaper_backup_path()
        # 写入config.json
        self.save_config()

    # 写入config.json
    def save_config(self): 
        try:
            with open(self.config_path, mode='wt', encoding="utf-8") as f1:
                json.dump(self.config, f1) # 将json写入文件
        except Exception as e:
            logging.warning(f"Warning accessing registry: {e}")

    # 获取Steam安装位置
    def get_steam_path(self): 
        try:
            aReg = reg.ConnectRegistry(None, reg.HKEY_CURRENT_USER)
            aKey = reg.OpenKey(aReg, r"Software\Valve\Steam")
            path = reg.QueryValueEx(aKey, "SteamPath")[0]
            reg.CloseKey(aKey)
            return path
        except Exception as e:
            logging.error(f"Error accessing registry: {e}")
            return None

    # 获取WallpaperEngine安装位置
    def get_wallpaper_path(self): 
        try:
            aReg = reg.ConnectRegistry(None, reg.HKEY_CURRENT_USER)
            aKey = reg.OpenKey(aReg, r"Software\WallpaperEngine")
            path = reg.QueryValueEx(aKey, "installPath")[0]
            reg.CloseKey(aKey)
            path_dir = os.path.dirname(path)
            return path_dir
        except Exception as e:
            logging.error(f"Error accessing registry: {e}")
            return None
        
    # 获取WallpaperEngine备份位置
    def get_wallpaper_backup_path(self): 
        backupPath = os.path.join(self.config['wallpaperPath'], 'projects\\backup')
        return backupPath
    
    # 选择一个文件夹
    def openFileDialog(self, path, boxText): 
        file_name = QFileDialog.getExistingDirectory(None, "选择一个文件夹", self.config[path])
        if file_name:
            self.config[path] = file_name
            boxText.setText(file_name)
            # 写入config.json
            self.save_config()

    # 获取WallpaperEngine config位置并读取
    def get_wallpaper_config_path(self, wallpaper_path): 
        wallpaper_config_path = os.path.join(wallpaper_path, 'config.json')
        try:
            with open(wallpaper_config_path, encoding="utf-8") as f1:
                res = json.load(f1) # 从文件读取json并反序列化
                print(res)
        except Exception as e:
            logging.error(f"Error accessing registry: {e}")

    def mklink_dir(self):
        pass

        # mklink /j "C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine\projects\myprojects" "E:\wallpaper_engine_myprojects"
        # mklink /j "C:\Program Files (x86)\Steam\steamapps\workshop\content\431960" "E:\wallpaper_engine"

