import os, shutil, json
from win32com.client import Dispatch
import logging

from .Config import config, get_project_json
from .main import convert_path, openMessageDialog, getDirSize, dirSizeToStr
from .Thread import WorkerThread
from PySide6.QtCore import Slot
shell = Dispatch("WScript.Shell")

list_notify = list()

GeneratedDirThread = WorkerThread()

# 生成快捷方式
def GeneratedLnk(shorcut, target):
    # 目标文件路径
    try:
        target = target
        shortcut = shell.CreateShortcut(shorcut + '.lnk')
        shortcut.TargetPath = convert_path(target)
        shortcut.Save()
    except Exception as e:
        print('======================================Error==============================================')
        print(shorcut, target, e)
        print('-' * 60)
        # 未开发，选择二级扫描
        list_notify.append(target)

def GeneratedDir(name, path):
    pass

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
    path_old = ""
    path_new = ""
    try:
        if path == "":
            # 转移地址, -> 备份
            path_new = os.path.join(config["backupPath"], obj["workshopid"])
        else:
            # 转移地址, -> path
            path_new = os.path.join(path, obj["workshopid"])

        if obj["source"] == "wallpaper":
            # 源地址: 工坊
            path_old = os.path.join(config['mklinkList'][0]["path"], obj["workshopid"])
        elif obj["source"] == "tempData":
            # 源地址: 工坊
            path_old = os.path.dirname(obj["project"])
        elif obj["source"] == "backup":
            # 源地址: 备份
            path_old = os.path.join(config["backupPath"], obj["workshopid"])

        if obj["source"] == "wallpaper":
            # 移动文件夹
            shutil.move(path_old, path_new)
            # 更新数据
            obj["project"] = os.path.join(path_new, 'project.json')
            f1 = open(obj["project"], encoding='utf-8')
            objCopy = obj.copy()
            objCopy.update(json.load(f1)) # 合并，重合以f1为主
            f1.close()
            # 更新数据2
            obj["file"] = os.path.join(path_new, objCopy["file"])
            obj["source"] = "tempData"
            obj["invalid"] = False
            obj["previewsmall"] = obj["preview"] = os.path.join(path_new, objCopy["preview"])
            # 更新数据3
            objCopy.pop("previewsmall")
            objCopy.pop("project")
            objCopy.pop("source")
            objCopy.pop("invalid")
            f2 = open(obj["project"], 'w', encoding='utf-8')
            json.dump(objCopy, f2, ensure_ascii=False)
            f2.close()
            os.startfile(path_new)
            return obj
        # 创建目标文件夹
        if not os.path.isdir(path_new):
            os.makedirs(path_new)
        lists = os.listdir(path_old)
        if "filesize" not in obj:
            obj["filesize"] = getDirSize(path_old)
            obj["filesizelabel"] = dirSizeToStr(obj["filesize"])
        if path != "":
            obj["storagepath"] = path_new
        # print(os.path.join(path_new, 'project.json'))
        f1 = open(os.path.join(path_new, 'project.json'), 'w', encoding='utf-8')
        json.dump(obj, f1, ensure_ascii=False)
        f1.close()
        # 复制文件
        # shutil.copy2(obj["project"], path_new)
        os.remove(obj["project"])
        # 转移内容
        for item_name in lists:
            if item_name == 'project.json':
                continue
            else:
                # 移动文件
                shutil.move(os.path.join(path_old, item_name), path_new)
        # 创建备份快捷方式
        if path != "":
            GeneratedDirNas(path, obj["workshopid"])
        # openMessageDialog(f'转移完成:{obj["workshopid"]}')
    except Exception as e:
        logging.error(f"转移内容失败: {e}")
        # openMessageDialog(str(e), 'error')

# @Slot(bool) # @Slot(str)
# def handle_running_update(i): # 接收信号
#     print(f'# 接收信号 {i}')
#     openMessageDialog(f'转移完成')
# GeneratedDirThread.running_update.connect(handle_running_update)