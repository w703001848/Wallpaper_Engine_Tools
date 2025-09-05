import logging  # 引入logging模块
import os, json
import time
import winreg as reg

from PySide6.QtWidgets import QLineEdit

from .main import checkEnvironment, getDirSize, dirSizeToStr, openFileDialog, openDirDialog

version = "1.2"
config_path = os.path.join(os.getcwd(), 'config.json')

# 首次执行初始化config
config = {
    "isDevelopment": checkEnvironment(), # 开发模式
    "version": "",
    "username": os.getlogin(), # 获取本机用户名
    "steamPath": "", # steam地址
    "wallpaperPath": "", # wallpaper地址
    "backupPath": "", # wallpaper备份地址
    "uiThumbnails": "", # wallpaper图片缓存位置
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
    "nasLink": "", # NAS备份
    "isCheckedScene": True, # 场景
    "isCheckedVideo": True, # 视频
    "isCheckedWeb": True, # 网页
    "isCheckedApplication": True, # 应用
    "isCheckedInvalid": True, # 失效
    "filterSize": 30, # 分页
    "sortCurrent": "subscriptiondate", # 订阅日期
}

temp_workshopcache = [] # 工坊壁纸数据
temp_folders = [] # 壁纸分类数据
temp_authorblocklistnames = [] # 拉黑名单

# 下标获取参数
def __getitem__(key):
    return config[key]

# 读取config.json
def get_config(): 
    global config
    try:
        with open(config_path, encoding="utf-8") as f1:
            data = json.load(f1)
            # 新版本config合并
            if len(data) != len(config):
                for key in config.keys():
                    if not data.get(key, ''): data[key] = config[key]
            # 清理历史遗弃字段
            if len(data) != len(config):
                for key in data.keys():
                    if not config.get(key, ''): del data[key]
            config = data
    except Exception as e:
        logging.warning(f"读取config.json: {e}")

# 写入config.json
def save_config(): 
    try:
        with open(config_path, mode='wt', encoding="utf-8") as f1:
            json.dump(config, f1) # 将json写入文件
            print("保存config")
    except Exception as e:
        logging.warning(f"写入config.json: {e}")
        
# 设置config.json
def set_config(key, obj): 
    global config
    try:
        if config[key] != obj:
            config[key] = obj
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
        return ""
    
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
        return ""
    
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
        return ""

# 获取WallpaperEngine订阅地址
def get_wallpaper_steam_path(): 
    try:
        mklink_steam = os.path.join(os.path.dirname(config['steamPath']), 'steamapps\\workshop\\content\\431960')
        if os.path.exists(mklink_steam):
            return mklink_steam
        else:
            raise Exception("当前steam文件夹下无法查询到壁纸订阅目录!", mklink_steam)
    except Exception as e:
        logging.error(f"获取Steam壁纸订阅地址: {e}")

# 获取WallpaperEngine config位置并读取
def get_wallpaper_config(): 
    global temp_authorblocklistnames, temp_folders
    try:
        # WallpaperEngine 壁纸分类目录，拉黑名单
        with open(os.path.join(os.path.dirname(config["wallpaperPath"]), 'config.json'), encoding="utf-8") as f2:
            res = json.load(f2) # 从文件读取json并反序列化
            temp_authorblocklistnames = res[config["username"]]["general"]["browser"]["authorblocklistnames"]
            temp_folders = res[config["username"]]["general"]["browser"]["folders"]
            return True
    except Exception as e:
        logging.error(f"获取WallpaperEngine config位置并读取: {e}")
    return False

# WallpaperEngine 工坊壁纸缓存
# 参数有发布id，后期可查看是否黑名单。
# 包含项目详细信息和图片缓存等
def get_workshopcache():
    global temp_workshopcache
    try:
        with open(os.path.join(os.path.dirname(config["wallpaperPath"]), 'bin/workshopcache.json'), encoding="utf-8") as f1:
            res = json.load(f1) # 从文件读取json并反序列化
            temp_workshopcache = res["wallpapers"]
            wallpaper_steam_path = config['mklinkList'][0]["path"]
            if not os.path.exists(wallpaper_steam_path):
                raise Exception("文件夹不存在!", wallpaper_steam_path)
            for item in os.listdir(wallpaper_steam_path):
                # 判断文件夹是否包含在工坊壁纸缓存
                if not len(list(filter(lambda obj: obj['workshopid'] == item, temp_workshopcache))):
                    dir_path = os.path.join(wallpaper_steam_path, item)
                    project_path = os.path.join(dir_path, 'project.json')
                    if os.path.exists(project_path):
                        with open(project_path, encoding="utf-8") as f1:
                            data = json.load(f1) # 从文件读取json并反序列化
                            size = getDirSize(dir_path)
                            temp_workshopcache.append(getProjectJson(dir_path, item, project_path, data, size)) 
                    else:
                        # 工坊文件夹存在，但缺少project.json文件，有空开发转移到备份文件夹
                        # 备份文件夹项目，每次打开更新时间戳，大小计算
                        print(f"查询到工坊壁纸目录未知项目加入工坊，project.json不存在! {project_path}", )
            return True
    except Exception as e:
        logging.error(f"获取WallpaperEngine 工坊壁纸缓存并读取: {e}")
    return False
        
# 获取文件夹内项目列表
def get_backupDirs():
    list = []
    backupPath = config['backupPath']
    if os.path.exists(backupPath):
        for item in os.listdir(backupPath):
            dir_path = os.path.join(backupPath, item)
            if os.path.exists(dir_path):
                project_path = os.path.join(dir_path, 'project.json')
                with open(project_path, encoding="utf-8") as f1:
                    data = json.load(f1) # 从文件读取json并反序列化
                    size = getDirSize(dir_path) if 'filesize' in data else 0
                    list.append(getProjectJson(dir_path, item, project_path, data, size))
    return list

def getProjectJson(dir_path, item, project_path, data, size):
    return {
        "allowmobileupload" : False,
        "authorsteamid" : '',
        "favorite" : False,
        "file" : os.path.join(dir_path, data["file"] if "file" in data else ""),
        "filesize" : size,
        "filesizelabel" : dirSizeToStr(size),
        "hasrating" : False,
        "ispreset" : False,
        "local" : False,
        "official" : False,
        "preview" : os.path.join(dir_path, data["preview"]),
        "previewsmall" : os.path.join(dir_path, data["preview"]),
        "project" : project_path,
        "rating" : 0,
        "ratingrounded" : 5.0,
        "status" : '',
        "subscriptiondate" : int(time.time()),
        "tags" : ','.join(data["tags"] if "tags" in data else []),
        "title" : data["title"],
        "type" : data["type"] if "type" in data else "",
        "updatedate" : int(time.time()),
        "workshopid" : item,
        "workshopurl" : '',

        "description" : data["description"] if "description" in data else None,
    }

# 获取WallpaperEngine 图片缓存位置
def get_wallpaper_ui_thumbnails(name): 
    return os.path.join(config['uiThumbnails'], name)

# 修改Steam安装位置
def set_steam_path(path):
    if path:
        set_config('steamPath', path)
        # 同步设置mklinkList Steam地址
        config['mklinkList'][0]["path"] = get_wallpaper_steam_path()
        return True
    else:
        return False

# 修改WallpaperEngine安装位置
def set_wallpaper_path(path):
    if path:
        set_config('wallpaperPath', path)
        # 同步设置 备份地址、图片缓存地址
        if not config['backupPath']:
            set_wallpaper_backup_path(get_wallpaper_backup_path())
            set_config('uiThumbnails', os.path.join(os.path.dirname(path), 'ui\\thumbnails'))
        return True
    else:
        return False

# 修改WallpaperEngine备份位置
def set_wallpaper_backup_path(path):
    if path:
        set_config('backupPath', path)
        # 同步设置mklinkList 备份地址
        config['mklinkList'][1]["path"] = path
        return True
    else:
        return False

# 设置文本框steam地址
def setSteamPath(lineEdit: QLineEdit):
    # path = openFileDialog(config.steamPath)
    __path = openFileDialog(config["steamPath"], "请选择steam.exe启动文件", "Steam (*.exe)")
    if __path:
        set_steam_path(__path)
        lineEdit.setText(__path)

# 设置文本框wallpaper地址
def setWallpaperPath(lineEdit: QLineEdit):
    # path = openDirDialog(config.wallpaperPath)
    __path = openFileDialog(config["wallpaperPath"], "请选择wallpaper_engine/launcher.exe启动文件", "Steam (*.exe)")
    if __path:
        set_wallpaper_path(__path)
        lineEdit.setText(__path)

# 设置文本框backup地址
def setBackupPath(lineEdit: QLineEdit):
    __path = openDirDialog(config["backupPath"])
    if __path:
        set_wallpaper_backup_path(__path)
        lineEdit.setText(__path)

# 查询是否存在并获取config.json
# if os.path.exists(config_path):
# 测试用
if config['isDevelopment'] and os.path.exists(config_path):
    get_config()

config['version'] = version

if not config['steamPath']:
    set_steam_path(os.path.abspath(get_steam_path_registry() + '/steam.exe'))

if not config['wallpaperPath']:
    set_wallpaper_path(os.path.abspath(get_wallpaper_path_registry() + '/launcher.exe'))

if config['wallpaperPath']:
    # 获取wallpaper_config数据
    get_wallpaper_config()
    get_workshopcache()

# print(f"steamPath:{version}")