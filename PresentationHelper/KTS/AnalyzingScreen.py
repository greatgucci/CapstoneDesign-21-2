import cv2
import keras.models
import numpy as np
import threading
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from keras.preprocessing.image import img_to_array



class AnalyzingScreen(QMainWindow):
    delay = 0.125
    def __init__(self, controller):
        super(AnalyzingScreen, self).__init__()
        loadUi("UI/analyzing.ui", self)
        self.controller = controller



    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("AnalyzingSceneLoaded")
        # delay analyze start
        threading.Timer(self.delay, self.start_analyze).start()

    def start_analyze(self):
        self.controller.video_analyze_data = VideoAnalyzer().getData()
        # todo : 최주연님, 녹화된 음성 분석
        self.goto_analyzed()

    def goto_analyzed(self):
        self.controller.setScreen(3)

class VideoAnalyzer:
    def __init__(self):
        face_detection = cv2.CascadeClassifier('files/haarcascade_frontalface_default.xml')
        emotion_classifier = keras.models.load_model('files/emotion_model.hdf5', False)
        cap = cv2.VideoCapture('Output/video.mp4')
        fps = cap.get(cv2.CAP_PROP_FPS);
        self.face_data_list = []
        fpsCount = 0;

        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                fpsCount += 1;
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
                    time = fpsCount/fps
                    self.face_data_list.append(FaceData(time, preds))
            else:
                cap.release()
                break

    def getData(self):
        return self.face_data_list


class FaceData:
    emotion_types = ["화남", "역겨움", "공포", "행복", "슬픔", "놀람", "안정됨"]

    def __init__(self, time, emotions):
        self.time = time
        self.emotions = emotions
