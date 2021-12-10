import time
import cv2
from PyQt5.QtCore import QTimer
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow
from threading import Thread
from PyQt5 import QtGui
from AnalyzingScreen import FaceData

## 오디오 
import pyaudio
import wave
from Path import Path


class RewatchScreen(QMainWindow):
    screen_w = 1600
    screen_h = 900
    drawInterval = int((1 / 24) * 1000)

    def __init__(self, controller):
        super(RewatchScreen, self).__init__()
        loadUi(Path.path_RewatchScreen(), self)
        self.controller = controller

    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("RewatchScreen Loaded")
        self.streaming = 0
        self.videoView = VideoStream()
        self.audioView = AudioView(self, self.controller.sound_analyze_data, self.controller.record_second)
        self.draw_start()

    def draw_start(self):
        self.face_data = self.controller.video_analyze_data
        self.face_data_index = 0

        self.start_time = time.time()
        self.timer = QTimer(self)
        self.timer.setInterval(self.drawInterval)
        self.timer.timeout.connect(self.draw_event)
        self.timer.start()

    def draw_event(self):
        if self.videoView.isPlay:
            threshold = 20
            highlight = "font: 16pt \"예스 고딕 레귤러\"; background-color:rgba(0, 0, 0, 125); Color : red"
            normal = "font: 16pt \"예스 고딕 레귤러\"; background-color:rgba(0, 0, 0, 125); Color : white"
            text_ui_list = [self.video_text0, self.video_text1, self.video_text2, self.video_text3,
                            self.video_text4, self.video_text5, self.video_text6]

            img = cv2.cvtColor(self.videoView.read(), cv2.COLOR_BGR2RGB)
            qt_img = QtGui.QImage(img, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888)
            pxm = QPixmap.fromImage(qt_img)
            self.video.setPixmap(pxm.scaled(self.screen_w, self.screen_h))
            self.video.update()

            text_updated = False

            if self.face_data_index < len(self.face_data) and self.videoView.get_frame() >= self.face_data[self.face_data_index].frame:
                self.face_data_index += 1
                text_updated = True

            if self.face_data_index < len(self.face_data) and text_updated:
                data = self.face_data[self.face_data_index]
                self.video_text_title.setText("표정")
                for i in range(len(data.emotion_types)):
                    val = int(data.emotions[i] * 100)
                    text_ui_list[i].setText(data.emotion_types[i] + " : " + str(val) + "%")
                    if val >= threshold:
                        text_ui_list[i].setStyleSheet(highlight)
                    else:
                        text_ui_list[i].setStyleSheet(normal)

        if not self.audioView.isPlay and not self.videoView.isPlay:
            self.timer.disconnect()
            self.timer.stop()
            self.controller.setScreen(0)




#오디오 출력 스레드
class AudioView:

    def __init__(self, window, audio_data, record_seconds):
        from RecordScreen import CHUNK
        self.isPlay = True
        self.window = window
        self.record_seconds = record_seconds
        #todo : 이거에 set string 하시면 됩니다.
        self.audio_data = audio_data

        self.open = True
        self.p = pyaudio.PyAudio()
        self.CHUNK = CHUNK
        self.PATH = Path.path_SoundOuput()

        self.wf = wave.open(self.PATH, 'rb')

        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                        channels=self.wf.getnchannels(),
                        rate=self.wf.getframerate(),
                        output=True)

        self.viewThread = Thread(target=self.play, args=())
        self.viewThread.start()

    def play(self):
        from RecordScreen import  DURATION, PER

        audio_text0 = self.window.audio_text0
        audio_text1 = self.window.audio_text1 
        audio_text2 = self.window.audio_text2
        
        data = self.wf.readframes(self.CHUNK)
        vol_n = 0
        sub_n = 0
        check_vol_text = False
        check_sub_text = False
        highlight_r = "font: 16pt \"예스 고딕 레귤러\"; background-color:rgba(0, 0, 0, 125); Color : red"
        highlight_b = "font: 16pt \"예스 고딕 레귤러\"; background-color:rgba(0, 0, 0, 125); Color : skyblue"
        normal = "font: 16pt \"예스 고딕 레귤러\"; background-color:rgba(0, 0, 0, 125); Color : white"
        sub_normal = "font: 20pt \"예스 고딕 레귤러\"; background-color:rgba(0, 0, 0, 125); Color : white"
        
        start = time.time()

        while data != b'':
            # 흘러간 시간 측정
            check_time = time.time() - start
            self.window.volume_text_title.setText("볼륨")
            self.window.spm_text_title.setText("빠르기")

            # check_time이 DURATION의 배수일 경우
            if int(check_time) % DURATION == 0 and check_vol_text == False:
                if int(check_time) > 0:
                    if vol_n < (self.record_seconds // DURATION):
                        vol_text = str((vol_n+1)*DURATION)+'초: '+str(round(self.audio_data[0][vol_n], 1))+'dB\n'
                        audio_text0.setText(vol_text)
                        if round(self.audio_data[0][vol_n], 1) < 53.9:
                            audio_text0.setStyleSheet(highlight_b)
                        elif round(self.audio_data[0][vol_n], 1) > 69.0:
                            audio_text0.setStyleSheet(highlight_r)
                        else:
                            audio_text0.setStyleSheet(normal)
                        check_vol_text = True
                        vol_n += 1
                    else:
                        pass
            # check_time이 DURATION의 배수가 아닐 경우
            if check_time > (vol_n+1)*DURATION:
                check_vol_text = False

            # check_time이 PER의 배수일 경우
            if int(check_time) % PER == 0 and check_sub_text == False:
                if int(check_time) > 0:
                    tempo_text = str((sub_n)*PER)+'초: '+str(round(self.audio_data[2][sub_n-1], 2))+'\n'
                    audio_text1.setText(tempo_text)
                    audio_text1.setStyleSheet(normal)
                    if round(self.audio_data[2][sub_n-1], 1) < 5.33:
                        audio_text1.setStyleSheet(highlight_b)
                    elif round(self.audio_data[2][sub_n-1], 1) > 6.01:
                        audio_text1.setStyleSheet(highlight_r)
                if sub_n > self.record_seconds // PER:
                    sub_text = self.audio_data[1][-1]
                else:
                    sub_text = self.audio_data[1][sub_n]
                if len(sub_text)>= 50:
                    sub_text = sub_text[:50]+'\n'+sub_text[50:]
                audio_text2.setText(sub_text)
                audio_text2.setStyleSheet(sub_normal)
                check_sub_text = True
                sub_n += 1
            # check_time이 PER의 배수가 아닐 경우
            if check_time > sub_n*PER:
                check_sub_text = False
            self.stream.write(data)
            data = self.wf.readframes(self.CHUNK)

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.isPlay = False

        
class VideoStream:
    def __init__(self):
        self.camera = cv2.VideoCapture(Path.path_VideoOutput())
        read, self.img = self.camera.read()
        self.isPlay = True
        self.camThread = Thread(target=self.record, args=())
        self.camThread.start()

    def record(self):
        while self.isPlay:
            read, self.img = self.camera.read()
            if read:
                time.sleep(0.03)
            else:
                self.isPlay = False
                self.camera.release()

    def read(self):
        return self.img

    def get_frame(self):
        return self.camera.get(cv2.CAP_PROP_POS_FRAMES)




