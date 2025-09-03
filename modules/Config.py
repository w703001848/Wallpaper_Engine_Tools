import logging  # 引入logging模块
import os
import json
import winreg as reg

from PySide6.QtWidgets import QLineEdit

from .main import checkEnvironment, openFileDialog, openDirDialog, openMessageDialog

config_path = os.path.join(os.getcwd(), 'config.json')

# 首次执行初始化config
boolSetConfig = False
config = {
    "isDevelopment": checkEnvironment(), # 开发模式
    "version": "1.1",
    "username": os.getlogin(), # 获取本机用户名
    "steamPath": "", # steam地址
    "wallpaperPath": "", # wallpaper地址
    "backupPath": "", # wallpaper备份地址
    "repkgPath": "", # 记录上次提取RePKG路径
    # "isCheckedRePKGClear": False, # 是否清空RePKG上次输出
    "mklinkList": [{
        "name": "订阅",
        "path": "",
        "path_new": ""
    }, {
        "name": "备份",
        "path": "",
        "path_new": ""
    }], # mklink历史新增
    # "isCheckedScene": True, # 场景
    # "isCheckedVideo": False, # 视频
    # "isCheckedWeb": False, # 网页
    # "isCheckedApplication": False, # 应用
    # "isCheckedInvalid": False, # 失效
}
    
# 下标获取参数
def __getitem__(key):
    return config[key]

# 读取config.json
def get_config(): 
    global config
    try:
        with open(config_path, encoding="utf-8") as f1:
            config = json.load(f1) # 从文件读取json并反序列化
    except Exception as e:
        logging.warning(f"读取config.json: {e}")

# 写入config.json
def save_config(): 
    global boolSetConfig
    try:
        with open(config_path, mode='wt', encoding="utf-8") as f1:
            json.dump(config, f1) # 将json写入文件
            boolSetConfig = False
    except Exception as e:
        logging.warning(f"写入config.json: {e}")
        
# 设置config.json
def set_config(key, obj): 
    global config, boolSetConfig
    try:
        if config[key] != obj:
            config[key] = obj
            boolSetConfig = True
    except Exception as e:
        logging.warning(f"设置config.json: {e}")

# 注册表获取Steam安装位置
def get_steam_path_registry(): 
    try:
        __aReg = reg.ConnectRegistry(None, reg.HKEY_CURRENT_USER)
        __aKey = reg.OpenKey(__aReg, r"Software\Valve\Steam")
        __path = reg.QueryValueEx(__aKey, "SteamPath")[0]
        reg.CloseKey(__aKey)
        if os.path.exists(__path):
            return __path
        else:
            return ''
    except Exception as e:
        logging.error(f"获取Steam安装位置: {e}")
        return None
    
# 注册表获取WallpaperEngine安装位置
def get_wallpaper_path_registry(): 
    try:
        __aReg = reg.ConnectRegistry(None, reg.HKEY_CURRENT_USER)
        __aKey = reg.OpenKey(__aReg, r"Software\WallpaperEngine")
        __path = reg.QueryValueEx(__aKey, "installPath")[0]
        reg.CloseKey(__aKey)
        __path_dir = os.path.dirname(__path)
        if os.path.exists(__path_dir):
            return __path_dir
        else:
            return ''
    except Exception as e:
        logging.error(f"获取WallpaperEngine安装位置: {e}")
        return None
    
# 获取WallpaperEngine备份位置
def get_wallpaper_backup_path(): 
    try:
        __path_dir = os.path.join(os.path.dirname(config['wallpaperPath']), 'projects\\backup')
        if os.path.exists(__path_dir):
            return __path_dir
        else:
            return ''
    except Exception as e:
        logging.error(f"获取WallpaperEngine备份位置: {e}")
        return None

# 获取WallpaperEngine订阅地址
def get_wallpaper_steam_path(): 
    try:
        mklink_steam = os.path.join(os.path.dirname(config['steamPath']), 'steamapps\\workshop\\content\\431960')
        if os.path.exists(mklink_steam):
            return mklink_steam
        else:
            openMessageDialog('当前steam文件夹下无法查询到壁纸订阅目录!')
            raise Exception("当前steam文件夹下无法查询到壁纸订阅目录!", mklink_steam)
    except Exception as e:
        logging.error(f"获取Steam软链接地址: {e}")
        return None

# 修改Steam安装位置
def set_steam_path(path):
    if path:
        set_config('steamPath', path)
        config['mklinkList'][0]["path"] = get_wallpaper_steam_path()
    return True

# 修改WallpaperEngine安装位置
def set_wallpaper_path(path):
    if path:
        set_config('wallpaperPath', path)
        if not config['backupPath']:
            set_wallpaper_backup_path(get_wallpaper_backup_path())
    return True

# 修改WallpaperEngine备份位置
def set_wallpaper_backup_path(path):
    if path:
        set_config('backupPath', path)
        config['mklinkList'][1]["path"] = path

# 设置文本框steam地址
def setSteamPath(lineEdit: QLineEdit):
    # path = openFileDialog(config.steamPath)
    __path = openFileDialog(config["steamPath"], "请选择steam.exe启动文件", "Steam (*.exe)")
    if __path:
        set_steam_path(__path)
        # 写入config.json
        save_config()
        lineEdit.setText(__path)

# 设置文本框wallpaper地址
def setWallpaperPath(lineEdit: QLineEdit):
    # path = openDirDialog(config.wallpaperPath)
    __path = openFileDialog(config["wallpaperPath"], "请选择wallpaper_engine/launcher.exe启动文件", "Steam (*.exe)")
    if __path:
        set_wallpaper_path(__path)
        # 写入config.json
        save_config()
        lineEdit.setText(__path)

# 设置文本框backup地址
def setBackupPath(lineEdit: QLineEdit):
    __path = openDirDialog(config["backupPath"])
    if __path:
        set_wallpaper_backup_path(__path)
        # 写入config.json
        save_config()
        lineEdit.setText(__path)

            


# 查询是否存在并获取config.json
if os.path.exists(config_path):
# 测试用
# if config['isDevelopment'] and os.path.exists(config_path):
    get_config()

if not config['steamPath']:
    boolSetConfig = set_steam_path(os.path.abspath(get_steam_path_registry() + '/steam.exe'))
if not config['wallpaperPath']:
    boolSetConfig = set_wallpaper_path(os.path.abspath(get_wallpaper_path_registry() + '/launcher.exe'))
if boolSetConfig:
    # 写入config.json
    save_config()

# print(f"steamPath:{steamPath}")