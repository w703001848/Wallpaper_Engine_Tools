import os, logging

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLineEdit, QTableWidget, QLabel

from modules.Config import set_config, save_config

# output_filter_img = "filtered-images"
# output_ideal_img = "ideal-images"
output = "output"
imageSuffix = ["bmp", "jpg", "png", "tif", "gif", "pcx", "tga", "exif", 
                    "fpx", "svg", "psd", "cdr", "pcd", "dxf", "ufo", "eps",
                    "ai", "raw", "WMF", "webp", "avif", "apng"]
filter_size_criteria = 500
pathExecuted = "" # 提取地址
updataPath = "" # 防止重复刷新

# 运行RePKG命令，提取文件到output文件夹
def runRepkg():
    try:
        # 修改工作目录
        if os.path.exists(output):
            clearDir(output)
            # os.removedirs(output)
        os.system(r'repkg extract -e tex -s -o ./{} "{}"'.format(output, pathExecuted))
    except Exception as e:
        logging.error(f"Warning accessing registry 请检查路径是否正确: {e}")
    os.chdir(os.getcwd())
# 筛选提取的文件，整合到对应文件夹

def followWork():
    # if not os.path.exists(output_ideal_img):
    #     os.makedirs(output_ideal_img)
    # if not os.path.exists(output_filter_img):
    #     os.makedirs(output_filter_img)
    # clearDir(output_ideal_img, output_filter_img)
    for fileName in os.listdir(output):
        if fileName.split(".")[-1] in imageSuffix:
            file = os.path.join(output, fileName)
            size = os.path.getsize(file) / 1024
            print("{} -> size:{:.3f}KB".format(fileName, size))
            # if size > filter_size_criteria:
            #     shutil.copy(file, output_ideal_img)
            # else:
            #     shutil.copy(file, output_filter_img)
        else:
            os.remove(os.path.join(os.getcwd(), output, fileName))

# 清理文件
def clearDir(*dirs):
    chdir = os.getcwd()
    for dir in dirs:
        os.chdir(os.path.join(chdir, dir))
        for file in os.listdir("./"):
            if os.path.isdir(file):
                clearDir(file)
                os.removedirs(file)
            else:
                os.remove(file)
    # 重置工作目录
    os.chdir(chdir)

def processItem(path, startfile=False):
    global pathExecuted
    if path:
        pathExecuted = path
    else:
        return False
    runRepkg()
    print("\n{:*^150}\n".format("已完成pkg文件提取"))     
    followWork()
    print("\n{:*^150}\n".format("已完成图片提取，开始清理不必要文件"))
    # clearDir(output)
    # os.removedirs(output)
    # print("代码工作完成，请查看：\n{}\n{}".format(
    #     os.path.join(os.getcwd(), output_ideal_img),
    #     os.path.join(os.getcwd(), output_filter_img)))
    
    if startfile:
        set_config("repkgPath", pathExecuted)
        save_config()
        # 打开资源管理器
        os.startfile(os.path.join(os.getcwd(), output))
    return True

# repkg列表更新
def updataRepkg(path, lineEdit: QLineEdit, tableWidget: QTableWidget):
    global updataPath
    print(f"{updataPath}:{path}")
    if path != '' and updataPath != path: # 防止重复刷新
        print("updataRepkg刷新")
        updataPath = path
        lineEdit.setText(path)
        setRepkgImgData(tableWidget)

# repkg图表生成
def setRepkgImgData(tableWidget: QTableWidget):
    dirPath = os.path.join(os.getcwd(), output)
    if not os.path.exists(dirPath):
        return
    data = os.listdir(dirPath)
    tableWidget.horizontalHeader().setStretchLastSection(True) # 表格自适应
    # tableWidget.horizontalHeader().setVisible(True) # 隐藏头
    # tableWidget.verticalHeader().setVisible(True) # 隐藏侧边
    colMax = 3
    tableWidget.setColumnCount(colMax)
    tableWidget.setRowCount(0) # 清空
    tableWidget.setRowCount(int(len(data) / colMax + 0.9))
    size = 199
    row = 0
    col = 0
    tableWidget.setColumnWidth(0, size)
    tableWidget.setColumnWidth(1, size)
    tableWidget.setColumnWidth(2, size)
    tableWidget.setRowHeight(0, size)
    for index, item in enumerate(data):
        imgPath = os.path.join(dirPath, item)
        boxItem = QLabel()
        boxItem.setMinimumSize(QSize(size, size))
        boxItem.setMaximumSize(QSize(size, size))
        boxItem.setScaledContents(True)
        boxItem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pic = QPixmap(imgPath)
        boxItem.setPixmap(pic)
        tableWidget.setCellWidget(row, col, boxItem)
        col += 1
        if col >= colMax:
            col = 0
            row += 1
            tableWidget.setRowHeight(row, size)
