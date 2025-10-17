from PySide6.QtCore import QThread, Signal, Slot
import time
 
class WorkerThread(QThread):
    """
    多线程

    :param None/int time: 可为空，执行下次运行间隔最小时间（秒）代码运行耗时包括在内。
                    可能大于time，则直接运行，否则等待间隔。
    
    Main API
    ========
    run(...): 启用多线程后运行中的代码
    
    setFun(...): 设置需要后台运行的函数代码,内置于run中

    start(...): 启动线程,开始执行run

    pause_or_resume(...): 改变当前状态，暂停

    stop(...): time不为空时,用于结束运行

    wait(...): 等待线程安全结束

    running_update.connect(...): 绑定信号,运行结束触发,return Bool

    count_update.connect(handle_count_update): 绑定信号,time传入时启用,每次间隔触发,return int

    @Slot(int)、@Slot(str):装饰器 识别函数用于接收信号
    def handle_count_update(self, i): # 用于接收信号绑定的函数
    
    Constants
    ---------
    running: 启用状态
    
    paused: 暂停状态
    """
    count_update = Signal(int)  # 创建一个信号，用于发送进度
    running_update = Signal(object)  # 创建一个信号，用于发送结果
    
    def __init__(self, time = None):
        super().__init__()
        self.running = False
        self.paused = False
        self.time = time
        self.fun = None

    def run(self):
        self.running = True
        if self.time:
            timer = time.time()
            while self.running:
                if not self.paused:
                    if time.time() - timer >= self.time:
                        self.count_update.emit(timer)
                        if self.fun is not None:
                            self.fun()
                        timer = time.time()
            self.running = False
        elif self.fun is not None:
            data = self.fun()
            self.running = False
            self.running_update.emit(data)

    def setFun(self, fun):
        self.fun = fun

    def pause_or_resume(self):
        self.paused = not self.paused

    def stop(self):
        self.running = False
        self.paused = False
        # self.wait() # 等待线程安全结束

    # 使用1
    # progressBar.setRange(0,5) # 设置进度为 5 个步骤（阶段）
    # # progressBar.setRange(0,0) # 进度条会显示忙碌指示符
    # # progressBar.reset() # 重置当前进度
    # self.counter_thread = WorkerThread(lambda:fun_xxx, self.progressBar)
    # @Slot(int) # @Slot(str)
    # def handle_count_update(self, i): # 接收信号
    #     progressBar.setValue(i)
    #     print(f'# 接收信号 {i}')
    #     openMessageDialog(f'转移完成')
    # self.counter_thread.running_update.connect(handle_running_update)
    
    # 使用2
    # self.counter_thread = WorkerThread(lambda:fun_xxx)
    # self.counter_thread.count_update.connect(self.handle_count_update)

    # @Slot(int) # @Slot(str)
    # def handle_count_update(self, i): # 接收信号
    #     if self.counter_thread.running:
    #         print(i)
    # def handle_start_thread(self, i):
    #     self.counter_thread.start()
    # def handle_toggle_update(self, i): # 暂停
    #     self.counter_thread.pause_or_resume()
    #     代码...
    # def handle_stop_update(self, i):
    #     self.counter_thread.stop()
    #     self.counter_thread.wait() # 等待线程安全结束
    #     代码...