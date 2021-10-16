import time
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow
from threading import Thread
from PyQt5 import QtGui
import cv2

#UI
#texts : audio_data , video_data
#screen : view
#slider : slider

class RewatchScreen(QMainWindow):
    screen_w = 1600
    screen_h = 900

    def __init__(self, controller):
        super(RewatchScreen, self).__init__()
        loadUi("UI/rewatch.ui", self)
        self.controller = controller

    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("RewatchScreen Loaded")
        VideoView(self.view)
        #Play Audio Thread
        self.draw_text()



    def draw_text(self):
        # todo : draw analyzed face data
        # todo : draw audio data
        return

#영상 출력 스레드
class VideoView:
    screen_w = 1600
    screen_h = 900
    stopped = False

    def __init__(self, graphic):
        self.graphic = graphic
        self.viewThread = Thread(target=self.drawEvent, args=())
        self.viewThread.start()

    def drawEvent(self):
        cap = cv2.VideoCapture('Output/video.mp4')
        interval = 1/cap.get(cv2.CAP_PROP_FPS)
        print(cap.get(cv2.CAP_PROP_FPS))
        while cap.isOpened():
            time_start = time.time()
            ret, img = cap.read()
            if ret:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                qt_img = QtGui.QImage(img, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888)
                pxm = QPixmap.fromImage(qt_img)
                self.graphic.setPixmap(pxm.scaled(self.screen_w, self.screen_h))
                self.graphic.update()
                wait_time = interval - (time.time() - time_start)
                if wait_time > 0:
                    time.sleep(wait_time)
            else:
                cap.release()
                break
