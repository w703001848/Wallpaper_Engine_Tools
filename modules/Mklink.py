import os, logging
import shutil

from PySide6.QtWidgets import QInputDialog, QListWidget

from .main import openMessageDialog, openStartfile, openDirDialog
from .Config import config

# 软链接生成
def createSymbolicLink(path_old, path_new):
    try:
        # 重命名原目录
        pathOldBack = path_old + '_back'
        os.rename(path_old, pathOldBack)
        # 软链接生成原地址目录不能存在，存在执行删除
        if os.path.exists(path_old):
            shutil.rmtree(path_old)
        # 生成软链接
        os.symlink(path_new, path_old)
        print(f"成功创建符号链接：{path_old} -> {path_new}")
        return True
    except Exception as e:
        logging.error(f"创建符号链接失败:{e}")
    return False

# 软链接回退
def backSymbolicLink(path_old):
    try:
        openStartfile(os.path.dirname(path_old))
        if os.path.exists(path_old):
            os.remove(path_old)
            # 重命名原目录
            pathOldBack = path_old + '_back'
            os.rename(pathOldBack, path_old)
            return True
    except Exception as e:
        logging.error(f"回退符号链接失败:{e}")
    return False

# 生成
def mklinkCreate(index):
    if index < 0:
        return False
    obj = config["mklinkList"][index]
    dir_path = obj["path"]
    dir_path_new = openDirDialog(obj["path_new"] or dir_path, "选择要转移的目标空文件夹")
    if dir_path_new: 
        # openStartfile(os.path.dirname(dir_path))
        if openMessageDialog(f"{dir_path}{os.linesep}转移至{os.linesep}{dir_path_new}", "tip"):
        # print("用户点击了确定")
            if createSymbolicLink(dir_path, dir_path_new):
                return dir_path_new
    return False

# 回退
def mklinkBack(index):
    data = config["mklinkList"]
    dir_path = data[index]['path']
    dir_path_new = data[index]['path_new']
    if dir_path_new: 
        if openMessageDialog(f"请确认{os.linesep}{dir_path_new}{os.linesep}回退至{os.linesep}{dir_path}", "tip"):
            return backSymbolicLink(dir_path, dir_path_new)
    return False

# 新增
def mklinkNew():
    remark, ok = QInputDialog.getText(None, '新增软链接', '请输入备注 例：备份')
    if ok:
        dir_path = openDirDialog(None, "选择要转移的目标空文件夹")
        if dir_path: 
            mklinkList = config["mklinkList"]
            obj = {
                "remark": remark,
                "path": dir_path,
                "path_new": ""
            }
            mklinkList.append(obj)
            return obj
    return False
        
# Mklink列表数据加载
def updateMklinkList(listWidget: QListWidget):
    if len(config["mklinkList"]) != listWidget.count():
        print('Mklink列表加载数据')
        for item in config["mklinkList"]:
            listWidget.addItem(f"标注:{item['remark']}{os.linesep}{item['path']}{os.linesep}{item['path_new'] or '未生成'}")
        listWidget.setCurrentRow(1) # 选中
