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

from Path import Path
# 수정
import time
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
        self.audioView = AudioView(self, self.controller.sound_analyze_data)

    def on_stream_end(self):
        if not self.videoView.isPlay and not self.audioView.isPlay:
            self.controller.setScreen(0)


#오디오 출력 스레드
class AudioView:

    def __init__(self, window, audio_data):
        from RecordScreen import  CHUNK, DURATION
        self.isPlay = True
        self.window = window
        #todo : 이거에 set string 하시면 됩니다.
        self.audio_text = window.audio_text 
        self.audio_tempo_text = window.audio_tempo_text 
        self.audio_sub_text = window.audio_sub_text

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

        self.start = 0
        self.viewThread = Thread(target=self.play, args=())
        self.viewThread.start()

    def play(self):
        from RecordScreen import  DURATION, PER, record_seconds
        
        self.start = time.time()
        data = self.wf.readframes(self.CHUNK)

        # 수정
        text = ''
        sub_text = ''
        tempo_text = ''
        n = 0
        sub_n = 0
        check_text = False
        check_sub_text = False
        while data != b'':
            # 흘러간 시간 측정
            check_time = time.time() - self.start
            
            # check_time이 5의 배수일 경우
            if check_time > 0 and int(check_time) % DURATION == 0 and check_text == False and n != (record_seconds // DURATION):
                text = str((n+1)*DURATION)+'초'+'\n'
                text += '볼륨: '+str(round(self.audio_data[0][n], 1))+'dB'+'\n'
                self.audio_text.setText(text)
                self.audio_text.update()
                check_text = True
                n += 1
                
            # check_time이 5의 배수가 아닐 경우
            if check_time > (n+1)*DURATION:
                check_text = False
            # check_time이 14의 배수일 경우
            if int(check_time) % PER == 0 and check_sub_text == False:
                tempo_text = str((sub_n+1)*PER)+'초'+'\n'
                if check_time > 0:
                    tempo_text += '빠르기: '+str(round(self.audio_data[2][n], 2))+'\n'
                    self.audio_tempo_text.setText(tempo_text)
                    self.audio_tempo_text.update()
                sub_text = self.audio_data[1][sub_n]
                self.audio_sub_text.setText(sub_text)
                self.audio_sub_text.update()
                check_sub_text = True
                sub_n += 1
                
            # check_time이 514의 배수가 아닐 경우
            if check_time > (n+1)*DURATION:
                check_sub_text = False
            
            self.stream.write(data)
            data = self.wf.readframes(self.CHUNK)

        self.stream.stop_stream()
        self.stream.close()
        print(self.audio_data[1])
        self.p.terminate()
        self.isPlay = False
        self.window.on_stream_end()
        # print('걸린 시간: ')
        # print(time.time()-self.start)


#영상 출력 스레드
class VideoView:
    screen_w = 1600
    screen_h = 900
    offset = 0.003

    def __init__(self, window, face_data):
        self.isPlay = True
        self.window = window
        self.video = window.video
        self.face_data = face_data
        self.viewThread = Thread(target=self.drawEvent, args=())
        self.viewThread.start()

    def drawEvent(self):
        cap = cv2.VideoCapture(Path.path_VideoOutput())
        interval = 1/cap.get(cv2.CAP_PROP_FPS)
        frame_cnt = 0
        face_data_index = 0
        threshold = 20
        highlight = "font: 16pt \"예스 고딕 레귤러\"; background-color:rgba(0, 0, 0, 125); Color : red"
        normal = "font: 16pt \"예스 고딕 레귤러\"; background-color:rgba(0, 0, 0, 125); Color : white"
        text_ui_list = [self.window.video_text0,self.window.video_text1,self.window.video_text2,self.window.video_text3,
                        self.window.video_text4,self.window.video_text5,self.window.video_text6]

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
                    self.window.video_text_title.setText("표정")
                    for i in range(len(data.emotion_types)):
                        val = int(data.emotions[i] * 100)
                        text_ui_list[i].setText(data.emotion_types[i] + " : " + str(val) + "%")
                        if (val >= threshold):
                            text_ui_list[i].setStyleSheet(highlight)
                        else:
                            text_ui_list[i].setStyleSheet(normal)

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
    



