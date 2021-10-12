import sys
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication
from KTS.AnalyzeScreen import AnalyzeScreen
from KTS.RecordScreen import RecordScreen
from KTS.WelcomeScreen import WelcomeScreen


class Controller:
    def __init__(self, mainwidget):
        self.mainWidget = mainwidget
        self.widgetList = [WelcomeScreen(self), RecordScreen(self), AnalyzeScreen(self)]
        mainwidget.addWidget(self.widgetList[0])
        mainwidget.addWidget(self.widgetList[1])
        mainwidget.addWidget(self.widgetList[2])
        mainwidget.setFixedHeight(900)
        mainwidget.setFixedWidth(1600)
        mainwidget.show()
        self.setScreen(0)

    def setScreen(self, index):
        self.mainWidget.setCurrentIndex(index)
        self.widgetList[index].onload()


app = QApplication(sys.argv)
Controller(QStackedWidget())

try:
    sys.exit(app.exec())
except:
    print("Exiting")
