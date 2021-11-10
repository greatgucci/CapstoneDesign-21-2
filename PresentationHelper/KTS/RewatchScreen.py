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
        VideoView(self.view, self.video_data, self.controller.video_analyze_data)
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

    def __init__(self, view_video, view_text, face_data):
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
                wait_time = interval - (time.time() - time_start)
                if wait_time > 0:
                    time.sleep(wait_time)
            else:
                cap.release()
                break
    # to do : 최주연        
    # 녹음파일 재생
    def play_audio(self):
        from RecordScreen import PATH, CHUNK
        
        wf = wave.open(PATH, 'rb')

        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(CHUNK)

        while data != b'':
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()

        p.terminate()



