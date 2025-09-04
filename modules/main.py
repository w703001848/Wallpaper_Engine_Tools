import logging  # 引入logging模块
import os
import keyboard
import time
from contextlib import contextmanager

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFileDialog, QMessageBox

# 防抖
class Debouncer(object):
    # 简单防抖
    def __init__(self, func, wait_time = 500):
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(wait_time)
        self.timer.timeout.connect(self.action)
        self.func = func
 
    # 触发计时
    def trigger(self):
        if not self.timer.isActive():
            self.timer.start()
        else:
            # 重新启动计时器以重置时间间隔
            self.timer.stop()
            self.timer.start()
    
    def action(self):
        print('计时结束开始处理')
        self.func()
    # 使用示例
    # debouncer = Debouncer(func, 500)  # 500毫秒的延迟

# 用于传参，默认函数
def func(*args, **kwargs):
    pass
 
# 代码耗时测试
@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        print(f"{label}: {end - start:.4f} seconds")
# 使用方式
# with timer("Function Execution"):
#     # 你的代码
#     for i in range(1000000):
#         pass

# Steam中解锁隐藏成就「30条命」‌,打开壁纸设置，切换到关于页面，点击解锁
# 上上下下左右左右ba回车
def Unlock_hidden_achievements():
    # 模拟键盘输入文本，需要先按下CTRL+SHIFT+ALT+K来激活文本输入模式（在一些应用程序中可能需要）
    keyboard.press_and_release('alt+tab') # 示例：激活文本输入模式（根据应用不同，可能需要不同的组合键）
    time.sleep(1)  # 等待文本输入模式激活
    keyegg = [
        "up",
        "up",
        "down",
        "down",
        "left",
        "right",
        "left",
        "right",
        "b",
        "a",
    ]
    for key in keyegg:
        keyboard.press_and_release(key)
        time.sleep(.5)
        # keyboard.write(key)  # 输入文本
    keyboard.press_and_release('enter')  # 按下Enter

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
def getDirSize(folder_path, isTop = True):
    if isTop:
        logging.warning('开启文件夹容量计算，占用性能建议关闭')
    total_size = 0
    with os.scandir(folder_path) as entries:
        for entry in entries:
            if entry.is_file():
                total_size += entry.stat().st_size
            elif entry.is_dir():
                total_size += getDirSize(entry.path, False)
    return total_size

# 容量转字符
def dirSizeToStr(size):
    size = size / 1024
    if size < 1024:
        return f"{size:.0f} KB"
    elif size < 1048576:
        return f"{size/1024:.0f} MB"
    else:
        return f"{size/1048576:.0f} GB"


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

