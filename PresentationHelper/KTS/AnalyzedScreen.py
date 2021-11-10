from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from AnalyzingScreen import FaceData

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
        self.print_audio_data(self.controller.sound_analyze_data)
        # todo : 영상 분석한 결과 출력

    def print_video_data(self, video_data):
        result = []
        total = [0]*len(FaceData.emotion_types)
        text = "캡쳐된 표정수 : "+str(len(video_data)) + "\n\n"
        text += "평균값\n"

        for i in range(len(video_data)):
            for j in range(len(FaceData.emotion_types)):
                total[j] += video_data[i].emotions[j]

        for i in range(len(FaceData.emotion_types)):
            result.append(int(total[i] / len(video_data) * 100))
            text += FaceData.emotion_types[i] + " : " + str(result[i]) + "%\n"

        if(result[0]>=25):
            self.video_suggestion.setText("너무 화나보여요")
        elif(result[4]>=25):
            self.video_suggestion.setText("너무 슬퍼 보여요..")
        elif(result[3]<=25):
            self.video_suggestion.setText("좀 더 웃으면 좋겠네요")
        else:
            self.video_suggestion.setText("훌륭 해요!")

        self.video_result.setText(text)
        self.video_result.update()

    # 분석 결과 유저에게 전달하는 함수
    def print_audio_data(self, sound_data):
        volume_text = '볼륨(dB): '
        for i in range(len(sound_data[0])):
            volume_text += str(round(sound_data[0][i], 1))+'초'
        volume_text += '\n'

        tempo_text = '빠르기(tempo): '
        for j in range(len(sound_data[1])):
            tempo_text += str(round(sound_data[1][j], 1))+'초'
        tempo_text += '\n'

        sub_text = '음성 인식: '
        for k in range(len(sound_data[2])):
            sub_text += sound_data[2][k]
        sub_text += '\n'

        self.audio_suggestion.setText("좀 더 차분하게 말하시면 좋겠네요!")
        self.audio_result.setText(volume_text+tempo_text+sub_text)
        self.audio_result.update()

    def goto_welcome(self):
        self.controller.setScreen(0)

    def goto_rewatch(self):
        self.controller.setScreen(4)
