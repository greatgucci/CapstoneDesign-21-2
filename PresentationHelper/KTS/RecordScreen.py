import sys
import time

import cv2
from PyQt5.QtGui import QPixmap
from threading import Thread
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtGui


class RecordScreen(QMainWindow):
    def __init__(self, controller):
        super(RecordScreen, self).__init__()
        loadUi("UI/record.ui", self)
        self.controller = controller
        self.endrecord.clicked.connect(self.goto_analyzing)

    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("RecordSceneLoaded")
        self.video = VideoStream()
        self.videoView = VideoView(self.view, self.video)
        #todo : 최주연님 , 음성 녹화

    def goto_analyzing(self):
        self.video.stop()
        self.videoView.stop()
        self.controller.setScreen(2)


#영상 보여주는 스레드가 따로 동작
class VideoView:
    screen_w = 1600
    screen_h = 900
    drawInterval = 1 / 30
    stopped = False

    def __init__(self, graphic, video):
        self.video = video
        self.graphic = graphic
        self.viewThread = Thread(target=self.drawEvent, args=())
        self.viewThread.start()

    def drawEvent(self):
        while not self.stopped:
            if self.video.streamStart:
                img = cv2.cvtColor(self.video.read(), cv2.COLOR_BGR2RGB)
                qt_img = QtGui.QImage(img, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888)
                pxm = QPixmap.fromImage(qt_img)
                self.graphic.setPixmap(pxm.scaled(self.screen_w, self.screen_h))
                self.graphic.update()
            time.sleep(self.drawInterval)

    def stop(self):
        self.stopped = True

# 영상 촬영, 저장을 위한 스레드가 따로 동작
class VideoStream:
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    cam_w = 1280
    cam_h = 720
    fps = 30
    streamStart = False
    stopped = False

    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_w)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_h)
        self.camera.set(cv2.CAP_PROP_FPS, self.fps)
        self.out = cv2.VideoWriter('Output/video.mp4', self.fourcc, self.fps, (self.cam_w, self.cam_h))
        self.camThread = Thread(target=self.record, args=())
        self.camThread.start()

    def record(self):
        while not self.stopped:
            read, self.img = self.camera.read()
            self.out.write(self.img)
            self.streamStart = True

    def read(self):
        return self.img

    def stop(self):
        self.stopped = True
        self.camera.release()
        self.out.release()
