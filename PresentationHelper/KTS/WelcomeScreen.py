from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow


class WelcomeScreen(QMainWindow):
    def __init__(self, controller):
        super(WelcomeScreen, self).__init__()
        loadUi("UI/welcome.ui", self)
        self.controller = controller
        self.record.clicked.connect(self.gotorecord)

    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("WelcomeSceneLoaded")

    def gotorecord(self):
        self.controller.setScreen(1)