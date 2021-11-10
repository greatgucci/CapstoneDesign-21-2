import sys
import threading
import time

import cv2
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
from logging import log

## 오디오 녹음에 필요한 상수
CHUNK = 512
# 16bit는 각 샘플의 크기
FORMAT = pyaudio.paInt16
CHANNELS = 1
# 샘플링 레이트(sr)
RATE = 22050
# record 함수 결과가 저장될 위치
PATH= "../files/audio"+"/output.wav"
# 데시벨, 템포 기준 초
DURATION = 5
# 음성 인식 기준 초
PER = 14

## 오디오 녹음에 필요한 전역 변수
decibels = []
record_seconds = 10

class RecordScreen(QMainWindow):
    def __init__(self, controller):
        super(RecordScreen, self).__init__()
        loadUi("../UI/record.ui", self)
        self.controller = controller
        self.endrecord.clicked.connect(self.goto_analyzing)

    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("RecordSceneLoaded")
        self.video = VideoStream()
        self.audio = AudioStream()
        self.videoView = VideoView(self.view, self.video)
        
    def goto_analyzing(self):
        self.video.stop()
        self.audio.stop()
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

# 음성 녹음을 위한 스레드
class AudioStream:

    global decibels

    def __init__(self):
        self.open = True
        self.p = pyaudio.PyAudio()
        self.CHUNK = CHUNK
        self.RATE = RATE
        self.FORMAT = FORMAT
        self.CHANNELS = CHANNELS
        self.PATH = PATH
        self.DURATION = DURATION
        self.frames = []

        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        self.thread = threading.Thread(target=self.record)
        self.thread.start()

    def record(self):
        print("녹음을 시작합니다")
        self.stream.start_stream()
        
        for i in range(0, int(self.RATE / self.CHUNK * record_seconds)):
            data = self.stream.read(CHUNK)
            self.frames.append(data)
            # print(i)
            if i % (int(self.RATE / self.CHUNK)*self.DURATION) == 0 and i > 0 and i < int(self.RATE / self.CHUNK)*record_seconds:
                # 볼륨 체크
                # 2는 sampling width in byte 
                rms = audioop.rms(data,2)
                # 데시벨 단위로 변환
                decibel = 20 * math.log(rms, 10)
                decibels.append(decibel)

    def stop(self):
        print("녹음을 종료합니다")

        # start_time = time.time()
        # end_time = time.time()
        # remain_time = record_seconds - int(end_time-start_time)
        # delete_time = remain_time // PER
        # print(remain_time)
        # if delete_time > 0 :
        #     frames = frames[:-(int(RATE / CHUNK)*PER*delete_time)]
        if self.open == True:
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

    def start(self):
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()


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

    
