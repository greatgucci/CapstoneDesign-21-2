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
        self.streaming = 0
        self.video = VideoView(self.view, self.video_data, self.controller.video_analyze_data)
        self.audio = AudioView()
        self.thread = Thread(target=self.stream_check_thread, args=())
        self.thread.start()


    def stream_check_thread(self):
        while self.video.isPlay or self.audio.isPlay:
            pass
        self.controller.setScreen(0)



#오디오 출력 스레드
class AudioView:

    def __init__(self):
        from RecordScreen import PATH, CHUNK
        self.isPlay = True

        self.open = True
        self.p = pyaudio.PyAudio()
        self.CHUNK = CHUNK
        self.PATH = PATH

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


#영상 출력 스레드
class VideoView:
    screen_w = 1600
    screen_h = 900
    offset = 0.0035

    def __init__(self, view_video, view_text, face_data):
        self.isPlay = True
        self.view_video = view_video
        self.view_text = view_text
        self.face_data = face_data
        self.viewThread = Thread(target=self.drawEvent, args=())
        self.viewThread.start()

    def drawEvent(self):
        cap = cv2.VideoCapture('Output/video.mp4')
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
                self.view_video.setPixmap(pxm.scaled(self.screen_w, self.screen_h))
                self.view_video.update()

                # draw text
                if (face_data_index < len(self.face_data)) and (frame_cnt >= self.face_data[face_data_index].frame):
                    data = self.face_data[face_data_index]
                    text = "표정\n"
                    for i in range(len(data.emotion_types)):
                        value = int(data.emotions[i] * 100)
                        text += data.emotion_types[i] + " : " + str(value) + "%\n"
                    self.view_text.setText(text)
                    self.view_text.update()
                    face_data_index += 1

                #wait
                wait_time = interval - (time.time() - time_start) - self.offset
                if wait_time > 0:
                    time.sleep(wait_time)
            else:
                cap.release()
                break

        self.isPlay = False
    



