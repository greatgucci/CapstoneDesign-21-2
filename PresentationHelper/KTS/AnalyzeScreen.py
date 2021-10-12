from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow


class AnalyzeScreen(QMainWindow):

    def __init__(self, controller):
        super(AnalyzeScreen, self).__init__()
        loadUi("UI/analyzed.ui", self)
        self.controller = controller
        self.towelcome.clicked.connect(self.gotowelcome)


    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("AnalyzeSceneLoaded")
        # todo : 태성 , 영상 분석한 결과 출력
        # todo : 최주연님, 음성 분석한 결과 출력

    def gotowelcome(self):
        self.controller.setScreen(0)