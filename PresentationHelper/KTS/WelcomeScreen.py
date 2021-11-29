from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow

from Path import Path


class WelcomeScreen(QMainWindow):

    def __init__(self, controller):
        super(WelcomeScreen, self).__init__()
        loadUi(Path.path_WelcomeScreen(), self)
        self.controller = controller
        self.record.clicked.connect(self.goto_record)

    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("WelcomeSceneLoaded")

    def goto_record(self):
        self.controller.record_second = int(self.second.toPlainText())
        self.controller.setScreen(1)