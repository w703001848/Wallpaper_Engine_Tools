import os, shutil, json
from win32com.client import Dispatch
import logging

from .Config import config
from .main import convert_path, openMessageDialog, getDirSize, dirSizeToStr
from .Thread import WorkerThread
from PySide6.QtCore import Slot
shell = Dispatch("WScript.Shell")

list_notify = list()

# 创建文件夹
def CreateDir(dir_path):
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

# 生成快捷方式
def GeneratedLnk(shorcut, target):
    # 目标文件路径
    try:
        shortcut = shell.CreateShortcut(shorcut + '.lnk')
        shortcut.TargetPath = convert_path(target)
        shortcut.Save()
    except Exception as e:
        print('======================================Error==============================================')
        print(shorcut, target, e)
        print('-' * 60)
        # 未开发，选择二级扫描
        list_notify.append(target)

# 生成快捷方式项目至备份
def GeneratedDirNas(path, name):
    dir_path_old = os.path.join(path, name) # 结合路径名与项目名
    dir_path_new = ""
    if config["mklinkList"][1]["path_new"] == "":
        dir_path_new = os.path.join(config["backupPath"], name)
    else:
        dir_path_new = os.path.join(config["mklinkList"][1]["path_new"], name)
    print('=' * 100)
    print('源文件/文件夹路径: %s' %(dir_path_old))
    try:
        # 创建目标文件夹
        if os.path.isdir(dir_path_new):
            logging.warning('已存在目标文件夹路径: %s' %(dir_path_new))
            list_notify.append(dir_path_old)
            return
        else:
            os.makedirs(dir_path_new)

        projectPath = os.path.join(dir_path_old, 'project.json')
        f1 = open(projectPath, encoding='utf-8')
        data = json.load(f1)
        f1.close()
        if "filesize" not in data:
            data["filesize"] = getDirSize(dir_path_old)
            data["filesizelabel"] = dirSizeToStr(data["filesize"])
            f1 = open(projectPath, 'w', encoding='utf-8')
            json.dump(data, f1, ensure_ascii=False)
            f1.close()

        # 复制project
        shutil.copy2(projectPath, os.path.join(dir_path_new, 'project.json'))

        try:
            target = os.path.join(dir_path_old, data["preview"])
            if not os.path.exists(target):
                raise Exception("无法查询到preview", dir_path_old)
            # 复制preview
            shutil.copy2(target, os.path.join(dir_path_new, data["preview"]))
        except Exception as e:
            logging.error(f'复制preview失败: {dir_path_old} - {e}')

        # 是否只生成'项目文件夹'快捷方式
        if "type" in data and data["type"].lower() == 'video':
            lists = os.listdir(dir_path_old)
            for item_name in lists:
                target = os.path.join(dir_path_old, item_name)
                txt_split = os.path.splitext(item_name)
                if txt_split[0] == "preview" or item_name == "project.json" or "Thumbs" in txt_split[0]:
                    continue
                else:
                    # print('拷贝: %s: %s: %s' %(target, dir_path_new, txt[0]))
                    GeneratedLnk(os.path.join(dir_path_new, txt_split[0]), target)
        else:
            GeneratedLnk(os.path.join(dir_path_new, name), dir_path_old)
        print('目标路径转移成功: %s' %(dir_path_new))
    except Exception as e:
        logging.error(f'目标路径转移失败: {e}')


# 转移项目
def MoveProject(obj, path = ""):
    # 转移地址, -> path
    path_new = os.path.join(path, obj["workshopid"])
    path_old = ""
    try:
        if obj["source"] == "wallpaper":
            # 源地址: 工坊
            path_old = os.path.join(config['mklinkList'][0]["path"], obj["workshopid"])
            obj["source"] = "tempData"
        elif obj["source"] == "tempData":
            # 源地址: 工坊
            path_old = os.path.dirname(obj["project"])
            obj["source"] = "backup"
        elif obj["source"] == "backup":
            # 源地址: 备份
            path_old = os.path.join(config["backupPath"], obj["workshopid"])
            obj["source"] = "backup"
            obj["storagepath"] = path_new
        # 移动文件夹
        shutil.move(path_old, path_new)
        # 更新数据
        projectPath = os.path.join(path_new, 'project.json')
        f1 = open(projectPath, encoding='utf-8')
        objCopy = obj.copy()
        objCopy.update(json.load(f1)) # 合并，重合以f1为主
        f1.close()
        # 更新数据3
        objCopy.pop("previewsmall")
        objCopy.pop("project")
        objCopy.pop("source")
        objCopy.pop("invalid")
        f2 = open(projectPath, 'w', encoding='utf-8')
        json.dump(objCopy, f2, ensure_ascii=False)
        f2.close()
        # 更新数据2
        if obj["source"] == "backup":
            GeneratedDirNas(path, obj["workshopid"])
        else:
            obj["project"] = projectPath
            obj["file"] = os.path.join(path_new, objCopy["file"])
            obj["previewsmall"] = obj["preview"] = os.path.join(path_new, objCopy["preview"])
            obj["invalid"] = False
        # os.startfile(path_new)
        print(obj)
        return obj
    except Exception as e:
        logging.error(f"转移内容失败: {e}")
        # openMessageDialog(str(e), 'error')