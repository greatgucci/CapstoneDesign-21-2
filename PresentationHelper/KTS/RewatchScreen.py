import time
import cv2
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow
from threading import Thread
from PyQt5 import QtGui
from AnalyzingScreen import FaceData

## 오디오 리플레이
import pyaudio
import wave
from Path import Path

class RewatchScreen(QMainWindow):
    screen_w = 1600
    screen_h = 900

    def __init__(self, controller):
        super(RewatchScreen, self).__init__()
        loadUi(Path.path_RewatchScreen(), self)
        self.controller = controller

    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("RewatchScreen Loaded")
        self.streaming = 0
        self.videoView = VideoView(self, self.controller.video_analyze_data)
        self.audioView = AudioView(self)


    def on_stream_end(self):
        if not self.videoView.isPlay and not self.audioView.isPlay:
            self.controller.setScreen(0)


#오디오 출력 스레드
class AudioView:

    def __init__(self, window):
        from RecordScreen import  CHUNK
        self.isPlay = True
        self.window = window
        self.audio_text = window.audio_text #todo : 이거에 set string 하시면 됩니다.

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
        data = self.wf.readframes(self.CHUNK)

        while data != b'':
            self.stream.write(data)
            data = self.wf.readframes(self.CHUNK)

        self.stream.stop_stream()
        self.stream.close()

        self.p.terminate()
        self.isPlay = False
        self.window.on_stream_end()


#영상 출력 스레드
class VideoView:
    screen_w = 1600
    screen_h = 900
    offset = 0.003

    def __init__(self, window, face_data):
        self.isPlay = True
        self.window = window
        self.video = window.video
        self.text = window.video_text
        self.face_data = face_data
        self.viewThread = Thread(target=self.drawEvent, args=())
        self.viewThread.start()

    def drawEvent(self):
        cap = cv2.VideoCapture(Path.path_VideoOutput())
        interval = 1/cap.get(cv2.CAP_PROP_FPS)
        frame_cnt = 0
        face_data_index = 0

        while cap.isOpened():
            time_start = time.time()
            ret, img = cap.read()
            if ret:
                frame_cnt += 1

                #draw image
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                qt_img = QtGui.QImage(img, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888)
                pxm = QPixmap.fromImage(qt_img)
                self.video.setPixmap(pxm.scaled(self.screen_w, self.screen_h))
                self.video.update()

                # draw text
                if (face_data_index < len(self.face_data)) and (frame_cnt >= self.face_data[face_data_index].frame):
                    data = self.face_data[face_data_index]
                    text = "표정\n"
                    for i in range(len(data.emotion_types)):
                        value = int(data.emotions[i] * 100)
                        text += data.emotion_types[i] + " : " + str(value) + "%\n"
                    self.text.setText(text)
                    self.text.update()
                    face_data_index += 1

                #wait
                wait_time = interval - (time.time() - time_start) - self.offset
                if wait_time > 0:
                    time.sleep(wait_time)
            else:
                cap.release()
                break

        self.isPlay = False
        self.window.on_stream_end()
    



