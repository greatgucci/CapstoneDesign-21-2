import cv2
import keras.models
import numpy as np
import threading
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from keras.preprocessing.image import img_to_array

## 오디오 분석
import librosa
import base64
import urllib3
import json
from pydub import AudioSegment


## 전역 변수
openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
accessKey = "62dbdbd8-e605-4035-a608-fb4563c92888"
# 수정
# audioFilePath = "src/output.wav"
languageCode = "korean"

splited_wavefile = []

class AnalyzingScreen(QMainWindow):
    delay = 0.125
    def __init__(self, controller):
        super(AnalyzingScreen, self).__init__()
        loadUi("../UI/analyzing.ui", self)
        self.controller = controller

    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("AnalyzingSceneLoaded")
        # delay analyze start
        threading.Timer(self.delay, self.start_analyze).start()

    # todo : 최주연님, 녹화된 음성 분석
    # 빠르기 분석
    def tempo_analysis(self):
        
        from RecordScreen import DURATION,PER, PATH, record_seconds
        
        tempos = []
        if record_seconds % DURATION == 0:
            per_duration = record_seconds // DURATION -1
        else:
            per_duration = (record_seconds // DURATION)

        for i in range(per_duration):
            y, sr = librosa.load(PATH, offset = DURATION*i, duration = DURATION, sr = 16000)
            onset_env = librosa.onset.onset_strength(y, sr = sr, aggregate=np.median)
            tempo, beats = librosa.beat.beat_track(onset_envelope = onset_env, sr = sr)
            tempos.append(tempo)

        return tempos

    # todo : 최주연님, 녹화된 음성 분석
    # 음성 인식 함수
    def get_subscription(self):
        from RecordScreen import PER, PATH, record_seconds
        
        global splited_wavefile
        
        subscription = []
        # 원본 wav파일 나누는 횟수
        repeat = record_seconds // PER
        if record_seconds % PER != 0:
            repeat += 1

        for i in range(repeat):
            t = 1000*PER # per sec
            new_audio = AudioSegment.from_wav(PATH)

            # 원본 wav 파일 나누기
            if i == repeat - 1:
                if repeat != record_seconds // PER:
                    new_audio = new_audio[t*i:t*i+(record_seconds % PER)*1000]
                else:
                    new_audio = new_audio[t*i:t*i*2+1]
            else:
                new_audio = new_audio[t*i:t*(i+1)]

            # 나눠진 파일 생성
            file_name = "../files/audio/{0}second{1}.wav".format(PER, i)
            splited_wavefile.append(file_name)
            new_audio.export(file_name, format = "wav")
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
            
            data = json.loads(response.data.decode("utf-8", errors = 'ignore'))
            subscription.append(data['return_object']['recognized'])
        return subscription

    def start_audio_analyze(self):
        # todo : 최주연님, 녹화된 음성 분석
        from RecordScreen import decibels
        
        # decibels를 data에 저장
        self.controller.sound_analyze_data.append(decibels)
        # tempo_analysis 결과 data에 저장
        self.controller.sound_analyze_data.append(self.tempo_analysis())
        # get_subscription 결과 data에 저장
        self.controller.sound_analyze_data.append(self.get_subscription())

    def start_analyze(self):
        self.controller.video_analyze_data = VideoAnalyzer().getData()
        
        self.start_audio_analyze()
        self.goto_analyzed()

    def goto_analyzed(self):
        self.controller.setScreen(3)

class VideoAnalyzer:
    def __init__(self):
        face_detection = cv2.CascadeClassifier('files/haarcascade_frontalface_default.xml')
        emotion_classifier = keras.models.load_model('../files/emotion_model.hdf5', False)
        cap = cv2.VideoCapture('Output/video.mp4')
        self.face_data_list = []
        frame_cnt = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_detection.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                frame_cnt += 1
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
            else:
                cap.release()
                break

    def getData(self):
        return self.face_data_list


class FaceData:
    emotion_types = ["화남", "역겨움", "공포", "행복", "슬픔", "놀람", "안정됨"]

    def __init__(self, frame, emotions):
        self.frame = frame
        self.emotions = emotions
