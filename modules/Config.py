import os, sys
import time, json
import logging  # 引入logging模块
import winreg as reg

from .main import checkEnvironment, getDirSize, dirSizeToStr

version = "1.7"
chair_path = os.getcwd() # 当前工作目录
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
        "remark": "订阅",
        "path": "",
        "path_new": ""
    }, {
        "remark": "备份",
        "path": "",
        "path_new": ""
    }], # mklink历史新增
    "nasLinkPath": "", # NAS备份IP地址
    "nasLink": [], # NAS备份
    "isCheckedScene": True, # 场景
    "isCheckedVideo": True, # 视频
    "isCheckedWeb": True, # 网页
    "isCheckedApplication": True, # 应用
    "isCheckedWallpaper": False, # 工坊
    "isCheckedBackup": False, # 备份
    "isCheckedInvalid": True, # 失效
    "isCheckedAuthorblock": True, # 黑名单
    "sortCurrent": "subscriptiondate", # 订阅日期
    "sortReverse": False, # 排序 正序
    "filterSize": 30, # 分页
    "displaySize": 160, # 显示大小
    "isFolders": True, # 是否开启同步wallpaper壁纸分类数据
    "folders": [], # 工坊分类数据
    "unWorkshop": [], # 工坊失效壁纸
    "unWorkshopProject": [], # 工坊缺少project.json文件夹
    "workshopBackup": [], # 工坊壁纸备份数据
    "unBackupProject": [], # 备份缺少project.json文件夹
}

temp_authorblocklistnames = [] # 拉黑名单
temp_dependency = [] # 父级关联项目

# 下标获取参数
# def __getitem__(key):
#     return config[key]

# 读取config.json
def get_config(): 
    global config
    try:
        f1 = open(config_path, encoding="utf-8")
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
        f1.close()
    except Exception as e:
        logging.error(f"读取config.json: {e}")

# 写入config.json
def saveConfig(): 
    try:
        f1 = open(config_path, mode='wt', encoding="utf-8")
        json.dump(config, f1, ensure_ascii=False) # 将json写入文件
        print("保存config")
        f1.close()
    except Exception as e:
        logging.error(f"写入config.json: {e}")
        
# 设置config.json
def setConfig(key, obj): 
    global config
    try:
        if config[key] != obj:
            config[key] = obj
    except Exception as e:
        logging.error(f"设置config.json: {e}")

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
            print(f"WallpaperEngine订阅地址: {mklink_steam}")
            return mklink_steam
        else:
            raise Exception("当前steam文件夹下无法查询到壁纸订阅目录!", mklink_steam)
    except Exception as e:
        logging.error(f"获取Steam壁纸订阅地址: {e}")

# 获取WallpaperEngine config位置并读取 壁纸分类目录、拉黑名单
def get_wallpaper_config(): 
    global temp_authorblocklistnames
    try:
        f1 = open(os.path.join(os.path.dirname(config["wallpaperPath"]), 'config.json'), encoding="utf-8")
        res = json.load(f1) # 从文件读取json并反序列化
        temp_authorblocklistnames = res[config["username"]]["general"]["browser"]["authorblocklistnames"]
        if config["isFolders"]:
            setConfig('folders', res[config["username"]]["general"]["browser"]["folders"])
        f1.close()
        return True
    except Exception as e:
        logging.error(f"获取WallpaperEngine config位置并读取: {e}")
    return False

# WallpaperEngine 工坊壁纸缓存
def get_workshopcache():
    try:
        f1 = open(os.path.join(os.path.dirname(config["wallpaperPath"]), 'bin/workshopcache.json'), encoding="utf-8")
        res = json.load(f1) # 从文件读取json并反序列化
        f1.close()
        return res["wallpapers"]
    except Exception as e:
        logging.error(f"获取WallpaperEngine 工坊壁纸缓存并读取: {e}")
    return []

# 获取WallpaperEngine 图片缓存位置
# def get_wallpaper_ui_thumbnails(name): 
#     return os.path.join(config['uiThumbnails'], name)

# 新增壁纸缓存
def get_project_json(source, invalid, dir_name, dir_path, data, project_path):
    global temp_dependency # 父级关联项目
    obj = None
    # def generateProject():
    if data is None:
        size = getDirSize(dir_path)
        img = u":/img/dir.png" # qt资源图片地址
        obj = {
            "allowmobileupload" : False,
            "authorsteamid" : "",
            "dependency": "", # 父级壁纸
            "favorite" : False,
            "file": "",
            "filesize": size,
            "filesizelabel": dirSizeToStr(size),
            "hasrating" : False,
            "ispreset" : False,
            "local" : False,
            "official" : False,
            "preview" : img,
            "previewsmall" : img,
            "project" : project_path,
            "rating" : 0,
            "ratingrounded" : 5.0,
            "status" : "",
            "subscriptiondate" : int(time.time()),
            "tags" : "",
            "title" : dir_name,
            "type" : "dir",
            "updatedate" : int(time.time()),
            "workshopid" : dir_name,
            "workshopurl" : "",
            "invalid": invalid, # 自增，用于判断失效
            "source": source, # 自增，用于判断来源
            "storagepath": "", # 自增，用于判断是否转移其他存储位置
        }
    else:
        obj = data
        obj["allowmobileupload"] = False
        obj["authorsteamid"] = ""
        obj["favorite"] = True
        if "file" in data:
            obj["file"] = os.path.join(dir_path, data["file"])
        else: 
            obj["file"] = ""
        if "filesize" not in data:
            obj["filesize"] = getDirSize(dir_path)
        if "filesizelabel" not in data:
            obj["filesizelabel"] = dirSizeToStr(obj["filesize"])
        obj["hasrating"] = False
        obj["ispreset"] = False
        obj["local"] = False
        obj["official"] = False
        obj["preview"] = os.path.join(dir_path, data["preview"])
        obj["previewsmall"] = obj["preview"]
        obj["project"] = project_path
        obj["rating"] = 0
        obj["ratingrounded"] = 5.0
        obj["status"] = ''
        obj["subscriptiondate"] = int(time.time())
        if "tags" in data:
            obj["tags"] = ','.join(data["tags"])
        else:
            obj["tags"] = []
        if "type" in data:
            obj["type"] = data["type"]
        elif "dependency" in data:
            for itemDependency in temp_dependency:
                if itemDependency["workshopid"] == data["dependency"]:
                    obj["type"] = itemDependency["type"]
                    break
        else:
            obj["type"] = "Web"
        obj["updatedate"] = int(time.time())
        obj["workshopid"] = dir_name
        obj["workshopurl"] = os.path.join("steam://url/CommunityFilePage", dir_name)
        obj["invalid"] = invalid
        obj["source"] = source
        if "storagepath" not in data:
            obj["storagepath"] = ""
    return obj

# 参数有发布id，后期可查看是否黑名单。
# 包含项目详细信息和图片缓存等
def getWorkshop():
    global temp_dependency # 父级关联项目

    temp_workshopcache = get_workshopcache()
    # temp_workshopcache = []
    un_workshop = config['unWorkshop'] # 工坊失效壁纸
    un_project = config["unWorkshopProject"] # 工坊缺少project.json文件夹

    workshopBackup = config["workshopBackup"] # 工坊壁纸备份数据
    un_backup = config["unBackupProject"] # 备份缺少project.json文件夹

    wallpaper_steam_path = config['mklinkList'][0]["path"]
    backupPath = config["backupPath"]

    # 如果存在父级关联工坊壁纸缓存查询提取
    def search_workshopcache_dependency(obj):
        if "dependency" in obj:
            for item in temp_workshopcache:
                if item["workshopid"] == obj["dependency"]:
                    temp_dependency.append(item)
                    break

    if os.path.exists(wallpaper_steam_path):

        # 还原工作目录
        os.chdir(wallpaper_steam_path)
        # 清理缓存里工坊失效文件夹是否还存在
        if len(un_workshop):
            print(f"清理工坊失效壁纸、文件夹缓存：{len(un_workshop)}")
            count = 0
            while count < len(un_workshop): # 涉及删除操作用while
                item = un_workshop[count]
                if not os.path.exists(item["workshopid"]):
                    logging.warning(f'工坊未找到{item["workshopid"]}')
                    del un_workshop[count]
                else:
                    count += 1

        # 清理缓存里缺少project.json文件夹是否还存在
        if len(un_project):
            print(f"清理工坊失效壁纸、文件夹缓存：{len(un_project)}")
            count = 0
            while count < len(un_project): # 涉及删除操作用while
                item = un_project[count]
                if not os.path.exists(item["workshopid"]):
                    logging.warning(f'未找到{item["workshopid"]}')
                    del un_project[count]
                else:
                    count += 1
        # 还原工作目录
        os.chdir(chair_path)

        # 整合工坊数据
        workshop_dir = os.listdir(wallpaper_steam_path)
        # 排除缓存中的文件夹，减少计算量
        count = 0
        while count < len(workshop_dir):
            dir_name = workshop_dir[count]
            if len(list(filter(lambda item: item['workshopid'] == dir_name, un_project))):
                del workshop_dir[count]
            else:
                count += 1
        # 筛选是否已标记为工坊缓存，减少计算量
        for item in temp_workshopcache:
            item["invalid"] = False # 初始化失效
            item["source"] = 'wallpaper' # 初始化来源
            # 如果存在父级关联就查询提取
            search_workshopcache_dependency(item)

            # 判断工坊缓存是否存在文件夹
            count = 0
            while count < len(workshop_dir):
                dir_name = workshop_dir[count]
                if dir_name == item["workshopid"]:
                    del workshop_dir[count]
                    break
                else:
                    count += 1
        # 多出的文件夹载入工坊失效壁纸、文件夹缓存
        print(f"工坊缓存未识别：{len(workshop_dir)}")
        for dir_name in workshop_dir:
            dir_path = os.path.join(wallpaper_steam_path, dir_name)
            if not os.path.isdir(dir_path):
                logging.warning(f"工坊缓存文件夹 存在无法识别文件：{dir_path}")
                continue
            # 判断文件是否存已记录再工坊失效缓夹存中
            if len(list(filter(lambda item: item['workshopid'] == dir_name, un_workshop))):
                continue
            if len(list(filter(lambda item: item['workshopid'] == dir_name, un_project))):
                continue
            project_path = os.path.join(dir_path, "project.json")
            if os.path.exists(project_path):
                try:
                    f1 = open(project_path, encoding="utf-8")
                    data = json.load(f1) # 从文件读取json并反序列化
                    un_workshop.append(get_project_json('wallpaper', True, dir_name, dir_path, data, project_path))
                    f1.close()
                    logging.warning(f"工坊壁纸目录未知项目加入工坊: {project_path}")
                except Exception as e:
                    un_project.append(get_project_json('wallpaper', True, dir_name, dir_path, None, project_path))
                    logging.error(f"提取工坊壁纸project.json无法识别: {dir_name} {e}")
            else:
                # 工坊文件夹存在，但缺少project.json文件，有空开发转移到备份文件夹
                un_project.append(get_project_json('wallpaper', True, dir_name, dir_path, None, project_path))
                logging.warning(f"查询到工坊壁纸目录未知项目加入工坊，project.json不存在! {project_path}")
    else:
        logging.warning("工坊文件夹不存在!跳过查询", wallpaper_steam_path)
    
    if os.path.exists(backupPath):
        # 修改工作目录到备份文件夹
        os.chdir(backupPath)
            # 整合备份失效壁纸、文件夹
            # 清理缓存里备份缺少project.json文件夹是否还存在
        if len(un_backup):
            print(f"清理备份缺少project.json文件夹缓存：{len(un_backup)}")
            count = 0
            while count < len(un_backup): # 涉及删除操作用while
                item = un_backup[count]
                if not os.path.exists(item["workshopid"]):
                    logging.warning(f'备份未找到{item["workshopid"]}')
                    del un_backup[count]
                else:
                    count += 1
        # 清理缓存里备份文件夹是否还存在
        workshopBackup = config["workshopBackup"]
        if len(workshopBackup):
            print(f"清理备份缓存：{len(workshopBackup)}")
            count = 0
            while count < len(workshopBackup): # 涉及删除操作用while
                item = workshopBackup[count]
                if not os.path.exists(item["workshopid"]):
                    logging.warning(f'备份未找到{item["workshopid"]}')
                    del workshopBackup[count]
                else:
                    count += 1
        # 还原工作目录
        os.chdir(chair_path)

        backup_dir = os.listdir(backupPath)
        # 整合工坊备份数据
        print(f"备份文件夹列表长度：{len(backup_dir)}")
        # 筛选是否已加入缓存，减少计算量
        count = 0
        while count < len(backup_dir):
            dir_name = backup_dir[count]
            # 筛选文件夹是否存已记录再备份缺失project.json缓存中
            if len(list(filter(lambda item: item['workshopid'] == dir_name, un_backup))):
                del backup_dir[count]
            # 筛选文件夹是否存已记录再备份缓存中
            elif len(list(filter(lambda item: item['workshopid'] == dir_name, workshopBackup))):
                del backup_dir[count]
            else:
                count += 1
        # 需要存入备份缓存的项目：
        print(f"需要存入备份缓存的项目：{len(backup_dir)}")
        for dir_name in backup_dir:
            dir_path = os.path.join(backupPath, dir_name)
            if not os.path.isdir(dir_path):
                logging.warning(f"备份文件夹 存在无法识别文件：{dir_path}")
                continue
            project_path = os.path.join(dir_path, "project.json")
            if os.path.exists(project_path):
                try:
                    f1 = open(project_path, encoding="utf-8")
                    data = json.load(f1) # 从文件读取json并反序列化
                    search_workshopcache_dependency(data)
                    workshopBackup.append(get_project_json('backup', False, dir_name, dir_path, data, project_path))
                    f1.close()
                    # logging.warning(f"备份缓存新增: {project_path}")
                except Exception as e:
                    logging.error(f"备份project.json无法识别: {dir_name} {e}")
                    un_backup.append(get_project_json('backup', True, dir_name, dir_path, None, project_path))
            else:
                # 工坊文件夹存在，但缺少project.json文件，有空开发转移到备份文件夹
                logging.warning(f"查询到备份缺失project.json文件夹加入备份缓存: {project_path}")
                un_backup.append(get_project_json('backup', True, dir_name, dir_path, None, project_path))
    else:
        logging.warning("备份文件夹不存在!跳过查询", backupPath)

    print(f'父级关联缓存：{len(temp_dependency)}')
    # print(temp_dependency)
    return temp_workshopcache + un_workshop + un_project + workshopBackup + un_backup # 壁纸数据（已整合）

# 修改Steam安装位置
def setSteamPath(path):
    if path:
        setConfig('steamPath', path)
        # 同步设置mklinkList Steam地址
        config['mklinkList'][0]["path"] = get_wallpaper_steam_path()
        return True
    else:
        return False

# 修改WallpaperEngine安装位置
def setWallpaperPath(path):
    if path:
        setConfig('wallpaperPath', path)
        # 同步设置 备份地址、图片缓存地址
        if not config['backupPath']:
            setWallpaperBackupPath(get_wallpaper_backup_path())
            setConfig('uiThumbnails', os.path.join(os.path.dirname(path), 'ui\\thumbnails'))
        return True
    else:
        return False

# 修改WallpaperEngine备份位置
def setWallpaperBackupPath(path):
    print(f"WallpaperEngine备份位置: {path}")
    if path:
        setConfig('backupPath', path)
        # 同步设置mklinkList 备份地址
        config['mklinkList'][1]["path"] = path
        return True
    else:
        return False

# 查询是否存在并获取config.json
if os.path.exists(config_path):
# 测试用
# if config['isDevelopment'] and os.path.exists(config_path):
    get_config()

config['version'] = version

if not config['steamPath']:
    setSteamPath(os.path.abspath(get_steam_path_registry() + '/steam.exe'))

if not config['wallpaperPath']:
    setWallpaperPath(os.path.abspath(get_wallpaper_path_registry() + '/launcher.exe'))

if config['wallpaperPath']:
    # 获取wallpaper_config数据
    get_wallpaper_config()

print(f"版本:{version}")