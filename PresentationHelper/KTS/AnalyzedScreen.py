from PyQt5.QtGui import QColor
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from AnalyzingScreen import FaceData
from Path import Path

#UI
#texts : audio_result,audio_suggestion,video_result,video_suggestion
#buttons : to_rewatch,to_welcome, page_button
class AnalyzedScreen(QMainWindow):

    def __init__(self, controller):
        super(AnalyzedScreen, self).__init__()
        loadUi(Path.path_AnalyzedScreen(), self)
        self.controller = controller
        self.page_button.setText('->')
        self.page_button.clicked.connect(self.add_page)
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
        text_ui_list = [self.video_result0, self.video_result1, self.video_result2,
                        self.video_result3, self.video_result4, self.video_result5, self.video_result6]

        total = [0]*len(FaceData.emotion_types)
        self.video_result_title.setText("캡쳐된 표정수 : "+str(len(video_data)))

        for i in range(len(video_data)):
            for j in range(len(FaceData.emotion_types)):
                total[j] += video_data[i].emotions[j]

        for i in range(len(FaceData.emotion_types)):
            result.append(int(total[i] / len(video_data) * 100))
            text_ui_list[i].setText(FaceData.emotion_types[i] + " : " + str(result[i]) + "%")
            
        threshold = 20 #기준값
        highlight = "font: 20pt \"예스 고딕 레귤러\"; Color : red"
        normal = "font: 20pt \"예스 고딕 레귤러\"; Color : white"

        text_ui_list[0].setStyleSheet(normal)
        text_ui_list[3].setStyleSheet(normal)
        text_ui_list[4].setStyleSheet(normal)

        if(result[0] >= threshold):
            self.video_suggestion.setText("헉.. 너무 화나보여요")
            text_ui_list[0].setStyleSheet(highlight)
        elif(result[4] >= threshold):
            self.video_suggestion.setText("너무 슬퍼 보여요..")
            text_ui_list[4].setStyleSheet(highlight)
        elif(result[3] <= threshold):
            self.video_suggestion.setText("좀 더 웃어 보면 어떨까요?")
            text_ui_list[3].setStyleSheet(highlight)
        else:
            self.video_suggestion.setText("훌륭 해요!")


    # 오디오 분석 결과 유저에게 전달하는 함수
    def print_audio_data(self, sound_data):
        from RecordScreen import PER, record_seconds

        highlight_r = "font: 20pt \"예스 고딕 레귤러\"; Color : red"
        highlight_b = "font: 20pt \"예스 고딕 레귤러\"; Color : skyblue"
        normal = "font: 20pt \"예스 고딕 레귤러\"; Color : white"
        sub_normal = "font: 20pt \"예스 고딕 레귤러\"; Color : white"

        ## 볼륨
        volume_sum = 0.0
        for i in range(len(sound_data[0])):
            volume_sum += round(sound_data[0][i], 1)
        # DURATION 단위 평균
        volume_avg = round(volume_sum / len(sound_data[0]), 1)
        self.audio_result0.setText('볼륨(dB): '+str(volume_avg)+'\n')
        self.audio_result0.setStyleSheet(normal)

        volume_suggestion = '볼륨: '
        if volume_avg < 53.9:
            volume_suggestion += '좀 더 크게 말하시면 좋겠네요'
            self.audio_result0.setStyleSheet(highlight_b)
        elif volume_avg > 69:
            volume_suggestion += '좀 더 작게 말하시면 좋겠네요'
            self.audio_result0.setStyleSheet(highlight_r)
        else:
            volume_suggestion += '적당합니다'
        volume_suggestion += '\n'

        ## 빠르기
        sub_text_temp = ''
        for k in range(len(sound_data[1])):
            if k == 0:
                sub_text_temp += sound_data[1][k]
            else:
                sub_text_temp += ' '+sound_data[1][k]

        # 1초 단위 평균
        spm_avg = round(len(sub_text_temp) / record_seconds, 2)
        self.audio_result1.setText('빠르기(초당 음절수): '+str(spm_avg)+'\n')

        self.audio_result1.setStyleSheet(normal)

        spm_suggestion = '빠르기: '
        if spm_avg < 5.33:
            spm_suggestion += '좀 더 빠르게 말하시면 좋겠네요'
            self.audio_result1.setStyleSheet(highlight_b)
        elif spm_avg > 6.33:
            spm_suggestion += '좀 더 느리게 말하시면 좋겠네요'
            self.audio_result1.setStyleSheet(highlight_r)
        else:
            spm_suggestion += '적당합니다'
        spm_suggestion += '\n'

        ## 음성 인식
        sub_text = '음성 인식: '
        sub_text_title = sub_text
        m = 0
        n = 0
        # 30은 ui의 width와 매칭되는 글자수
        while True:
            # 첫번째 줄
            if m == 0:
                sub_text += sub_text_temp[0:30-len(sub_text_title)]+'\n'
                n += 30-len(sub_text_title)
            # 마지막 줄
            elif m == len(sub_text_temp) // 30 and len(sub_text_temp) % 30 != 0:
                # len(sub_text_temp) - len(sub_text_temp) % 30
                sub_text += sub_text_temp[n:len(sub_text_temp)]+'\n'
                break
            # 그 외
            else:
                sub_text += sub_text_temp[n:n+30]+'\n'
                n += 30
            m += 1

        self.audio_result2.setText(sub_text)
        self.audio_result2.setStyleSheet(sub_normal)
        self.audio_suggestion.setText(volume_suggestion+spm_suggestion+'\n')
        
    def add_page(self):
        # page 넘김 추가
        pass

    def goto_welcome(self):
        self.controller.setScreen(0)

    def goto_rewatch(self):
        self.controller.setScreen(4)
