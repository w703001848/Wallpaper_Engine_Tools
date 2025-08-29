import os, logging
from PySide6.QtWidgets import QMessageBox

class RePKGFun(object):
    # output_filter_img = "filtered-images"
    # output_ideal_img = "ideal-images"
    output = "output"
    imageSuffix = ["bmp", "jpg", "png", "tif", "gif", "pcx", "tga", "exif", 
                        "fpx", "svg", "psd", "cdr", "pcd", "dxf", "ufo", "eps",
                        "ai", "raw", "WMF", "webp", "avif", "apng"]
    filter_size_criteria = 500
    steamDirs = ""

    # def __init__(self):
    #     RePKGFun.steamDirs = ""

    # 运行RePKG命令，提取文件到output文件夹
    def runRepkg(self):
        try:
            # 修改工作目录
            if os.path.exists(RePKGFun.output):
                self.clearDir(RePKGFun.output)
                # os.removedirs(RePKGFun.output)
            os.system(r'repkg extract -e tex -s -o ./{} "{}"'.format(RePKGFun.output, RePKGFun.steamDirs))
            RePKGFun.pathExecuted = RePKGFun.steamDirs
        except Exception as e:
            logging.error(f"Warning accessing registry 请检查路径是否正确: {e}")
        os.chdir(os.getcwd())

    # 筛选提取的文件，整合到对应文件夹
    def followWork(self):
        # if not os.path.exists(RePKGFun.output_ideal_img):
        #     os.makedirs(RePKGFun.output_ideal_img)
        # if not os.path.exists(RePKGFun.output_filter_img):
        #     os.makedirs(RePKGFun.output_filter_img)
        # self.clearDir(RePKGFun.output_ideal_img, RePKGFun.output_filter_img)

        for fileName in os.listdir(RePKGFun.output):
            if fileName.split(".")[-1] in self.imageSuffix:
                file = os.path.join(RePKGFun.output, fileName)
                size = os.path.getsize(file) / 1024
                print("{} -> size:{:.3f}KB".format(fileName, size))
                # if size > self.filter_size_criteria:
                #     shutil.copy(file, RePKGFun.output_ideal_img)
                # else:
                #     shutil.copy(file, RePKGFun.output_filter_img)
            else:
                os.remove(os.path.join(os.getcwd(), RePKGFun.output, fileName))

    # 清理文件
    def clearDir(self, *dirs):
        chdir = os.getcwd()
        for dir in dirs:
            os.chdir(os.path.join(chdir, dir))
            for file in os.listdir("./"):
                if os.path.isdir(file):
                    self.clearDir(file)
                    os.removedirs(file)
                else:
                    os.remove(file)
        # 重置工作目录
        os.chdir(chdir)

    def processItem(self, path="", startfile=False):
        if path:
            RePKGFun.steamDirs = path
        elif RePKGFun.steamDirs == "":
            return
        self.runRepkg()
        print("\n{:*^150}\n".format("已完成pkg文件提取"))     
        self.followWork()
        print("\n{:*^150}\n".format("已完成图片提取，开始清理不必要文件"))
        # self.clearDir(RePKGFun.output)
        # os.removedirs(RePKGFun.output)

        # print("代码工作完成，请查看：\n{}\n{}".format(
        #     os.path.join(os.getcwd(), RePKGFun.output_ideal_img),
        #     os.path.join(os.getcwd(), RePKGFun.output_filter_img)))
        
        if startfile:
            # 打开资源管理器
            os.startfile(os.path.join(os.getcwd(), RePKGFun.output))
        return True
