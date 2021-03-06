import threading
import time

import cv2
from PyQt5.QtCore import QTimer

from PyQt5.QtGui import QPixmap
from threading import Thread
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtGui

## 오디오 녹음
import pyaudio
import audioop
import wave
import math

# from KTS.WelcomeScreen import WelcomeScreen
import WelcomeScreen
from Path import Path

from keras_preprocessing.image import img_to_array

## 오디오 녹음에 필요한 상수
CHUNK = 512
# 16bit는 각 샘플의 크기
FORMAT = pyaudio.paInt16
CHANNELS = 1
# 샘플링 레이트(sr)
RATE = 22050
# 데시벨, 템포 기준 초
DURATION = 5
# 음성 인식 기준 초
PER = 10

## 오디오 녹음에 필요한 전역 변수
decibels = []

class RecordScreen(QMainWindow):
    screen_w = 1600
    screen_h = 900
    drawInterval = int((1 / 24) * 1000)

    def __init__(self, controller):
        super(RecordScreen, self).__init__()
        loadUi(Path.path_RecordScreen(), self)
        self.controller = controller

    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("RecordSceneLoaded")
        self.video = VideoStream()
        self.audio = AudioStream(self,self.controller.record_second)

        self.video.start()
        self.audio.start()
        self.draw_start()

    def draw_start(self):
        self.start_time = time.time()
        self.timer = QTimer(self)
        self.timer.setInterval(self.drawInterval)
        self.timer.timeout.connect(self.draw_event)
        self.timer.start()

    def draw_event(self):
        img = cv2.cvtColor(self.video.read(), cv2.COLOR_BGR2RGB)
        qt_img = QtGui.QImage(img, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888)
        pxm = QPixmap.fromImage(qt_img)
        self.graphic.setPixmap(pxm.scaled(self.screen_w, self.screen_h))
        self.graphic.update()

        current_time = time.time() - self.start_time
        self.time.setText("시간 : " + str(int(current_time)))
        self.time.update()

        if self.audio.stopped:
            self.video.stop()
            self.audio.stop()
            self.timer.disconnect()
            self.timer.stop()
            self.controller.setScreen(2)

# 음성 녹음을 위한 스레드
class AudioStream:

    global decibels

    def __init__(self, window, record_seconds):
        self.window = window
        self.record_seconds = record_seconds
        # 삭제 안됨
        self.stopped = False

        self.open = True
        self.p = pyaudio.PyAudio()
        self.CHUNK = CHUNK
        self.RATE = RATE
        self.FORMAT = FORMAT
        self.CHANNELS = CHANNELS
        self.PATH = Path.path_SoundOuput()
        self.DURATION = DURATION
        self.frames = []
        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        self.stream.start_stream()

    def start(self):
        self.thread = threading.Thread(target=self.record)
        self.thread.start()

    def record(self):
        print("녹음을 시작합니다")
        # for i in range(0, int(self.RATE / self.CHUNK * self.record_seconds)):
        # 삭제 안됨
        i = 0
        while not self.stopped:
            if i == int(self.RATE / self.CHUNK * self.record_seconds):
                break

            data = self.stream.read(CHUNK)
            self.frames.append(data)
            if i % (int(self.RATE / self.CHUNK) * self.DURATION) == 0 and 0 < i < int(self.RATE / self.CHUNK) * self.record_seconds:
                # 볼륨 체크
                # 2는 sampling width in byte 
                rms = audioop.rms(data,2)
                if(rms > 0):
                    # 데시벨 단위로 변환
                    decibel = 20 * math.log(rms, 10)
                    decibels.append(decibel)
            # 삭제 안됨
            i += 1

        self.stopped = True

    def stop(self):
        if self.open == True:
            # 삭제 안됨
            self.open = False

            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            wf = wave.open(self.PATH, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.frames))
            wf.close()
        pass


# 영상 촬영, 저장을 위한 스레드가 따로 동작
class VideoStream:
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    cam_w = 640
    cam_h = 360
    fps = 30

    def __init__(self):
        # self.camera = cv2.VideoCapture(0)
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_w)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_h)
        self.camera.set(cv2.CAP_PROP_FPS, self.fps)
        self.out = cv2.VideoWriter('Output/video.mp4', self.fourcc, self.fps, (self.cam_w, self.cam_h))
        read, self.img = self.camera.read()
        self.stopped = False

    def start(self):
        self.camThread = Thread(target=self.record, args=())
        self.camThread.start()

    def record(self):
        while not self.stopped:
            read, self.img = self.camera.read()
            self.out.write(self.img)

    def read(self):
        return self.img

    def stop(self):
        self.stopped = True
        self.camThread.join()
        self.camera.release()
        self.out.release()

    
