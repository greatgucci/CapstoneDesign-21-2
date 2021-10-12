import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication
from KTS.WelcomeScreen import WelcomeScreen
from KTS.RecordScreen import RecordScreen
from KTS.AnalyzedScreen import AnalyzedScreen
from KTS.AnalyzingScreen import AnalyzingScreen


class Controller:
    video_analyze_data = []
    sound_analyze_data = []

    def __init__(self, mainwidget):
        self.mainWidget = mainwidget
        self.widgetList = [WelcomeScreen(self), RecordScreen(self), AnalyzingScreen(self), AnalyzedScreen(self)]
        mainwidget.addWidget(self.widgetList[0])
        mainwidget.addWidget(self.widgetList[1])
        mainwidget.addWidget(self.widgetList[2])
        mainwidget.addWidget(self.widgetList[3])
        mainwidget.setFixedHeight(900)
        mainwidget.setFixedWidth(1600)
        mainwidget.show()
        self.setScreen(0)

    def setScreen(self, index):
        self.mainWidget.setCurrentIndex(index)
        self.mainWidget.update()
        self.widgetList[index].onload()


# main
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'   # tensorflow error 메시지 제외하고 무시
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # tensorflow cpu 사용
app = QApplication(sys.argv)
Controller(QStackedWidget())

try:
    sys.exit(app.exec())
except:
    print("Exiting")
