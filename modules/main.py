import logging  # 引入logging模块
import os

from PySide6.QtWidgets import QFileDialog, QMessageBox

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
        return True
    elif ret == QMessageBox.Cancel:
        funCancel(ret)
        return False

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
        obj['size'] = getDirSize(obj['path']) if isSize else 0
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
                total_size += getDirSize(entry.path)
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

