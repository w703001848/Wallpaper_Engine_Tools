import logging  # 引入logging模块
import os
# import shutil

class RePKG(object):
    # output_filter_img = "filtered-images"
    # output_ideal_img = "ideal-images"
    output = "output"
    imageSuffix = ["bmp", "jpg", "png", "tif", "gif", "pcx", "tga", "exif", 
                        "fpx", "svg", "psd", "cdr", "pcd", "dxf", "ufo", "eps",
                        "ai", "raw", "WMF", "webp", "avif", "apng"]
    filter_size_criteria = 500

    def __init__(self):
        self.steamDirs = ""

    # 运行RePKG命令，提取文件到output文件夹
    def run_repkg(self):
        try:
            # 修改工作目录
            if os.path.exists(RePKG.output):
                self.clearDir(RePKG.output)
                # os.removedirs(RePKG.output)
            os.system(r'repkg extract -e tex -s -o ./{} "{}"'.format(RePKG.output, self.steamDirs))
        except Exception as e:
            logging.error(f"Warning accessing registry 请检查路径是否正确: {e}")
        os.chdir(os.getcwd())

    # 筛选提取的文件，整合到对应文件夹
    def follow_work(self):
        # if not os.path.exists(RePKG.output_ideal_img):
        #     os.makedirs(RePKG.output_ideal_img)
        # if not os.path.exists(RePKG.output_filter_img):
        #     os.makedirs(RePKG.output_filter_img)
        # self.clearDir(RePKG.output_ideal_img, RePKG.output_filter_img)

        for fileName in os.listdir(RePKG.output):
            if fileName.split(".")[-1] in self.imageSuffix:
                file = os.path.join(RePKG.output, fileName)
                size = os.path.getsize(file) / 1024
                print("{} -> size:{:.3f}KB".format(fileName, size))
                # if size > self.filter_size_criteria:
                #     shutil.copy(file, RePKG.output_ideal_img)
                # else:
                #     shutil.copy(file, RePKG.output_filter_img)
            else:
                os.remove(os.path.join(os.getcwd(), RePKG.output, fileName))

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

    def process_item(self):
        self.run_repkg()
        print("\n{:*^150}\n".format("已完成pkg文件提取"))     
        self.follow_work()
        print("\n{:*^150}\n".format("已完成图片提取，开始清理不必要文件"))
        # self.clearDir(RePKG.output)
        # os.removedirs(RePKG.output)

        # print("代码工作完成，请查看：\n{}\n{}".format(
        #     os.path.join(os.getcwd(), RePKG.output_ideal_img),
        #     os.path.join(os.getcwd(), RePKG.output_filter_img)))
        
        # 打开资源管理器
        os.startfile(os.path.join(os.getcwd(), RePKG.output))



# pk = RePKG()
# pk.process_item()