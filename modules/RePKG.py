import os, math, logging

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QTableWidget, QLabel

# output_filter_img = "filtered-images"
# output_ideal_img = "ideal-images"
output = "output"
imageSuffix = ["bmp", "jpg", "png", "tif", "gif", "pcx", "tga", "exif", 
                    "fpx", "svg", "psd", "cdr", "pcd", "dxf", "ufo", "eps",
                    "ai", "raw", "WMF", "webp", "avif", "apng"]
filter_size_criteria = 500
pathExecuted = "" # 提取地址
chdir = os.getcwd()
# # 使用方式
# def processItem(path):
#     res = runRepkg(path)
#     if res:
#         res = followWork()

#     # clearDir(output)
#     # os.removedirs(output)
#     # print("代码工作完成，请查看：\n{}\n{}".format(
#     #     os.path.join(os.getcwd(), output_ideal_img),
#     #     os.path.join(os.getcwd(), output_filter_img)))

# 运行RePKG命令，提取文件到output文件夹
def runRepkg(path):
    global pathExecuted, chdir
    try:
        # 修改工作目录
        os.chdir(chdir)
        if os.path.exists(output):
            clearDir(output)
            # os.removedirs(output)
        os.system(r'repkg extract -e tex -s -o ./{} "{}"'.format(output, path))
        pathExecuted = path
    except Exception as e:
        logging.error(f"error 请检查路径是否正确: {e}")
        return False
    print("\n{:*^150}\n".format("已完成pkg文件提取"))  
    return True

# 筛选提取的文件，整合到对应文件夹
def followWork():
    print(f"已完成pkg文件提取{pathExecuted}")
    try:
        # if not os.path.exists(output_ideal_img):
        #     os.makedirs(output_ideal_img)
        # if not os.path.exists(output_filter_img):
        #     os.makedirs(output_filter_img)
        # clearDir(output_ideal_img, output_filter_img)
        print("\n{:*^150}\n".format("开始清理不必要文件"))
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
        return True
    except Exception as e:
        logging.error(f"error 筛选提取的文件，整合到对应文件夹: {e}")
        return False

# 清理文件
def clearDir(*dirs):
    global chdir
    # chdir = os.getcwd()
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

temp_repkg_img_list = [] # 存放临时数据
def updateRepkgData(tableWidget: QTableWidget, update = True):
    global temp_repkg_img_list
    # 更新数据
    if update:
        dirPath = os.path.join(os.getcwd(), output)
        if not os.path.exists(dirPath):
            return
        temp_repkg_img_list.clear()
        list = os.listdir(dirPath)
        for index, item in enumerate(list):
            temp_repkg_img_list.append(os.path.join(dirPath, item))

    # repkg图表生成
    size, colMax = calculateQuantity(tableWidget.size().width() - 16, 3)
    tableWidget.setColumnCount(colMax)
    tableWidget.clearContents() # 清空
    tableWidget.setRowCount(math.ceil(len(temp_repkg_img_list) / colMax))
    tableWidget.setRowHeight(0, size)

    # 根据列数设置列宽
    i = 0
    while i < colMax:
        tableWidget.setColumnWidth(i, size)
        i += 1

    row = 0 # 计数行
    col = 0 # 计数列
    for index, imgPath in enumerate(temp_repkg_img_list):
        itemBox = QLabel()
        # itemBox.setMinimumSize(QSize(size, size))
        itemBox.setMaximumSize(QSize(size, size))
        # itemBox.setScaledContents(True)
        itemBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        itemBox.setPixmap(QPixmap(imgPath).scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        tableWidget.setCellWidget(row, col, itemBox)
        
        col += 1
        if col >= colMax:
            col = 0
            row += 1
            tableWidget.setRowHeight(row, size)

def calculateQuantity(widgetWidth, colMax):
    size = int(widgetWidth / colMax)
    if size > 240:
        size, colMax = calculateQuantity(widgetWidth, colMax + 1)
    # elif size < 180:
    #     colMax = colMax - 1
    #     size, _ = calculateQuantity(widgetWidth, colMax)
    print(f"Repkg更新 图size:{size} 列:{colMax}")
    return size, colMax
