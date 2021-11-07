from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from KTS.AnalyzingScreen import FaceData

#UI
#texts : audio_result,audio_suggestion,video_result,video_suggestion
#buttons : to_rewatch,to_welcome
class AnalyzedScreen(QMainWindow):

    def __init__(self, controller):
        super(AnalyzedScreen, self).__init__()
        loadUi("UI/analyzed.ui", self)
        self.controller = controller
        self.to_welcome.clicked.connect(self.goto_welcome)
        self.to_rewatch.clicked.connect(self.goto_rewatch)

    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("AnalyzeSceneLoaded")
        self.print_video_data(self.controller.video_analyze_data)
        # todo : 영상 분석한 결과 출력

    def print_video_data(self, video_data):
        total = [0]*len(FaceData.emotion_types)
        text = "캡쳐된 표정수 : "+str(len(video_data)) + "\n\n"
        text += "평균값\n"

        for i in range(len(video_data)):
            for j in range(len(FaceData.emotion_types)):
                total[j] += video_data[i].emotions[j]

        for i in range(len(FaceData.emotion_types)):
            result = int(total[i] / len(video_data) * 100)
            text += FaceData.emotion_types[i] + " : " + str(result) + "%\n"

        self.video_suggestion.setText("좀 더 웃으시면 좋겠네요!")
        self.video_result.setText(text)
        self.video_result.update()


    def goto_welcome(self):
        self.controller.setScreen(0)

    def goto_rewatch(self):
        self.controller.setScreen(4)
