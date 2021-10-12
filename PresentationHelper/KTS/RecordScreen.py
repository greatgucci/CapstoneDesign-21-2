import cv2
from PyQt5.QtGui import QPixmap
from threading import Thread
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore
from PyQt5 import QtGui


class RecordScreen(QMainWindow):
    def __init__(self, controller):
        super(RecordScreen, self).__init__()
        loadUi("UI/record.ui", self)
        self.video = RecordVideo(self.cam,self)
        self.controller = controller
        self.endrecord.clicked.connect(self.gotoanalyze)

    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("RecordSceneLoaded")
        self.video.start_recording()
        #todo : 최주연님 , 음성 녹화

    def gotoanalyze(self):
        self.video.stop()
        self.controller.setScreen(2)


class RecordVideo(QtCore.QObject):
    screen_w = 1600
    screen_h = 900
    drawInterval = 1000 / 30

    def __init__(self, graphic, parent=None):
        super(RecordVideo, self).__init__(parent)
        self.graphic = graphic
        self.drawRecording = True


    def start_recording(self):
        # 카메라 연결
        self.videoStream = VideoStream()

        #draw
        if self.drawRecording:
            # 타이머 세팅
            self.drawTimer = QtCore.QTimer()
            self.drawTimer.timeout.connect(self.drawEvent)
            self.drawTimer.start(self.drawInterval)

    def stop(self):
        self.videoStream.stop()
        self.drawTimer.stop()

    def drawEvent(self):
        if not self.videoStream.streamStart:
            return

        img = cv2.cvtColor(self.videoStream.read(), cv2.COLOR_BGR2RGB)
        qtImg = QtGui.QImage(img, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888)
        pxm = QPixmap.fromImage(qtImg)
        self.graphic.setPixmap(pxm.scaled(self.screen_w, self.screen_h))
        self.graphic.update()

# 영상 촬영, 저장을 위한 스레드가 따로 동작
class VideoStream:
    img = [0]
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    cam_w = 1280
    cam_h = 720
    streamStart = False

    def __init__(self):
        self.stopped = False
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_w)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_h)
        self.camThread = Thread(target=self.record, args=())
        self.camThread.start()
        self.out = cv2.VideoWriter('Output/video.mp4', self.fourcc, self.camera.get(cv2.CAP_PROP_FPS), (self.cam_w, self.cam_h))


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

