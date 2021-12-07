from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from AnalyzingScreen import FaceData
from Path import Path

class VideoAnalyzedScreen(QMainWindow):

    def __init__(self, controller):
        super(VideoAnalyzedScreen, self).__init__()
        loadUi(Path.path_VideoAnalyzedScreen(), self)

        self.controller = controller
        self.to_audioAnalyzed.clicked.connect(self.goto_audioAnalyzed)
        self.to_welcome.clicked.connect(self.goto_welcome)
        self.to_rewatch.clicked.connect(self.goto_rewatch)

    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("VideoAnalyzeSceneLoaded")
        self.print_video_data(self.controller.video_analyze_data)

    def print_video_data(self, video_data):
        result = []
        text_ui_list = [self.video_result0, self.video_result1, self.video_result2,
                        self.video_result3, self.video_result4, self.video_result5, self.video_result6]
        bar_ui_list = [self.progressBar0, self.progressBar1, self.progressBar2,
                        self.progressBar3, self.progressBar4, self.progressBar5, self.progressBar6]

        total = [0]*len(FaceData.emotion_types)
        self.video_result_title.setText("캡쳐된 표정수 : "+str(len(video_data)))

        for i in range(len(video_data)):
            for j in range(len(FaceData.emotion_types)):
                total[j] += video_data[i].emotions[j]

        for i in range(len(FaceData.emotion_types)):
            result.append(int(total[i] / len(video_data) * 100))
            text_ui_list[i].setText(FaceData.emotion_types[i] + " : " + str(result[i]) + "%")
            bar_ui_list[i].setValue(result[i])
            
        threshold = 20 #기준값
        over = "font: 20pt \"예스 고딕 레귤러\"; Color : red"
        low = "font: 20pt \"예스 고딕 레귤러\"; Color : skyblue"
        normal = "font: 20pt \"예스 고딕 레귤러\"; Color : white"

        text_ui_list[0].setStyleSheet(normal)
        text_ui_list[3].setStyleSheet(normal)
        text_ui_list[4].setStyleSheet(normal)

        if(result[0] >= threshold):
            self.video_suggestion.setText("헉.. 너무 화나보여요")
            text_ui_list[0].setStyleSheet(over)
        elif(result[4] >= threshold):
            self.video_suggestion.setText("너무 슬퍼 보여요..")
            text_ui_list[4].setStyleSheet(over)
        elif(result[3] <= threshold):
            self.video_suggestion.setText("좀 더 웃어 보면 어떨까요?")
            text_ui_list[3].setStyleSheet(low)
        else:
            self.video_suggestion.setText("훌륭 해요!")

    def goto_welcome(self):
        self.controller.setScreen(0)

    def goto_rewatch(self):
        self.controller.setScreen(5)

    def goto_audioAnalyzed(self):
        self.controller.setScreen(4)