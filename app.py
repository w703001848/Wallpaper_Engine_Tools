from PySide6.QtWidgets import QApplication, QWidget
from widgets import UI_MainForm
from modules import *

class MyWindow(QWidget, UI_MainForm):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setupUi(self)

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()