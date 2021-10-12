from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow


class AnalyzedScreen(QMainWindow):
    emotions = ["화남", "역겨움", "공포", "행복", "슬픔", "놀람", "안정됨"]

    def __init__(self, controller):
        super(AnalyzedScreen, self).__init__()
        loadUi("UI/analyzed.ui", self)
        self.controller = controller
        self.towelcome.clicked.connect(self.goto_welcome)


    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("AnalyzeSceneLoaded")
        self.print_video_data(self.controller.video_analyze_data)
        # todo : 영상 분석한 결과 출력

    def print_video_data(self, data):
        total = [0]*len(self.emotions)
        text = ""
        for i in range(len(data)):
            for j in range(len(self.emotions)):
                total[j] += data[i][j]

        for i in range(len(self.emotions)):
            result = round(total[i] / len(data), 3)
            text += self.emotions[i] + ":" + str(result) + "\n"

        self.video_result.setText(text)



    def goto_welcome(self):
        self.controller.setScreen(0)