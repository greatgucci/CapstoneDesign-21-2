import time

import cv2
import keras.models
import numpy as np
from PyQt5.uic import loadUi
from keras.preprocessing.image import img_to_array

## 오디오 분석
import base64
import urllib3
import json
import threading
from PyQt5.QtWidgets import QMainWindow
from Path import Path
from pydub import AudioSegment

import os

## 오디오 분석 전역 변수
openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
accessKey = "62dbdbd8-e605-4035-a608-fb4563c92888"
languageCode = "korean"

splited_wavefile = []
subscription = []

class AnalyzingScreen(QMainWindow):
    delay = 0.125
    def __init__(self, controller):
        super(AnalyzingScreen, self).__init__()
        loadUi(Path.path_AnalyzingScreen(), self)
        self.controller = controller

    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("AnalyzingSceneLoaded")
        # delay analyze start
        time.sleep(self.delay)
        self.start_analyze()

    def start_analyze(self):
        #분석 속도 개선을 위해 thread 분리
        self.audioAnalyzer = AudioAnalyzer(self.controller.record_second)
        self.videoAnalyzer = VideoAnalyzer()

        while self.audioAnalyzer.isAnalyzing:
            pass
        
        self.controller.video_analyze_data = self.videoAnalyzer.getData()
        self.controller.sound_analyze_data = self.audioAnalyzer.getData()
        
        self.goto_analyzed()

    def goto_analyzed(self):
        self.controller.setScreen(3)

class VideoAnalyzer:
    def __init__(self):
        self.isAnalyzing = True
        self.face_data_list = []
        self.analyze()

    def analyze(self):
        print("video analyze start\n")
        face_detection = cv2.CascadeClassifier(Path.path_Haarcascarde())
        emotion_classifier = keras.models.load_model(Path.path_EmotionModel(), False)
        cap = cv2.VideoCapture(Path.path_VideoOutput())
        

        frame_cnt = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_detection.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                
                if len(faces) > 0:
                    # For the largest image
                    face = sorted(faces, reverse=True, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
                    (fX, fY, fW, fH) = face
                    # Resize the image to 48x48 for neural network
                    roi = gray[fY:fY + fH, fX:fX + fW]
                    roi = cv2.resize(roi, (48, 48))
                    roi = roi.astype("float") / 255.0
                    roi = img_to_array(roi)
                    roi = np.expand_dims(roi, axis=0)
                    # Emotion predict
                    preds = emotion_classifier.predict(roi)[0]
                    self.face_data_list.append(FaceData(frame_cnt, preds))
                frame_cnt += 10
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_cnt)
            else:
                cap.release()
                break
        print("video analyze end\n")
        self.isAnalyzing = False

    def getData(self):
        return self.face_data_list

class FaceData:
    emotion_types = ["화남", "역겨움", "공포", "행복", "슬픔", "놀람", "안정됨"]

    def __init__(self, frame, emotions):
        self.frame = frame
        self.emotions = emotions

class AudioAnalyzer:

    def __init__(self, record_seconds):
        self.isAnalyzing = True
        self.record_seconds = record_seconds
        self.data = []
        self.thread = threading.Thread(target=self.analyzeAudio, args=())
        self.thread.start()

    def analyzeAudio(self):

        from RecordScreen import decibels
        print("audio analyze start\n")
        # 볼륨 분석 결과 저장
        self.data.append(decibels)
        # 음성 인식 결과 저장
        self.data.append(self.get_subscription())
        # 빠르기 분석 결과 저장
        self.data.append(self.tempo_analysis())
        print("audio analyze end\n")
        self.isAnalyzing = False

    ## 녹화된 음성 분석
    def tempo_analysis(self):
        from RecordScreen import PER

        global subscription

        spm_per_sec = []
        for i in range(len(subscription)):
            # 평균값으로 초당 빠르기 분석
            spm_per_sec.append(len(subscription[i])/PER)
        return spm_per_sec

    def get_subscription(self):
        from RecordScreen import PER

        global splited_wavefile, subscription

        # 원본 wav파일 나누는 횟수
        repeat = self.record_seconds // PER
        if self.record_seconds % PER != 0:
            repeat += 1
        for i in range(repeat):
            # ms -> s
            t = 1000 * PER  
            new_audio = AudioSegment.from_wav(Path.path_SoundOuput())

            # 원본 wav 파일 나누기
            if repeat != 1:
                if i == repeat - 1:
                    if repeat != self.record_seconds // PER:
                        new_audio = new_audio[t * i:t * i + (self.record_seconds % PER) * 1000]
                    else:
                        new_audio = new_audio[t * i:t * i * 2 + 1]
                else:
                    new_audio = new_audio[t * i:t * (i + 1)]
            else:
                new_audio = new_audio[0:]

            # 나눠진 파일 생성
            file_name = Path.path_SoundDistributedFile(PER,i)
            splited_wavefile.append(file_name)
            new_audio.export(file_name, format="wav")
            audioFilePath_ = file_name

            # 음성 인식
            file = open(audioFilePath_, "rb")
            audioContents = base64.b64encode(file.read()).decode("utf8")
            file.close()

            requestJson = {
                "access_key": accessKey,
                "argument": {
                    "language_code": languageCode,
                    "audio": audioContents
                }
            }

            http = urllib3.PoolManager()
            response = http.request(
                "POST",
                openApiURL,
                headers={"Content-Type": "application/json; charset=UTF-8"},
                body=json.dumps(requestJson)
            )

            data = json.loads(response.data.decode("utf-8", errors='ignore'))
            subscription.append(data['return_object']['recognized'])

        for i in range(repeat):
            os.remove("Output/{0}second{1}.wav".format(PER, i))
        
        return subscription

    def getData(self):
        return self.data
