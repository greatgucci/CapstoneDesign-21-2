from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from AnalyzingScreen import FaceData
from Path import Path

#UI
#texts : audio_result,audio_suggestion,video_result,video_suggestion
#buttons : to_rewatch,to_welcome
class AnalyzedScreen(QMainWindow):

    def __init__(self, controller):
        super(AnalyzedScreen, self).__init__()
        loadUi(Path.path_AnalyzedScreen(), self)
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
        from RecordScreen import PER, record_seconds

        sub_text_temp = ''
        for k in range(len(sound_data[1])):
            sub_text_temp += sound_data[1][k]

        # 평균값
        volume_sum = 0.0
        # tempo_sum = 0.0
        for i in range(len(sound_data[0])):
            volume_sum += round(sound_data[0][i], 1)
            # tempo_sum += round(sound_data[1][i], 1)

        volume_avg = round(volume_sum / len(sound_data[0]), 1)
        # tempo_avg = round(tempo_sum / len(sound_data[0]), 1)
        spm_per_sec_avg = round(len(sub_text_temp) / record_seconds, 2)
        
        volume_text = '볼륨(dB): '+str(volume_avg)+'\n'
        # tempo_text = '빠르기(tempo): '+str(tempo_avg)+'\n'
        spm__per_sec_text = '빠르기(초당 음절수): '+str(spm_per_sec_avg)+'\n'

        volume_suggestion = '볼륨: '
        # 수정
        if volume_avg < 55:
            volume_suggestion += '좀 더 크게 말하시면 좋겠네요'
        elif volume_avg > 70:
            volume_suggestion += '좀 더 작게 말하시면 좋겠네요'
        volume_suggestion += '\n'

        # 수정
        spm_per_sec_suggestion = '빠르기: '
        if spm_per_sec_avg < 5.33:
            spm_per_sec_suggestion += '좀 더 빠르게 말하시면 좋겠네요'
        elif spm_per_sec_avg > 6.33:
            spm_per_sec_suggestion += '좀 더 느리게 말하시면 좋겠네요'
        spm_per_sec_suggestion += '\n'

        sub_text = '음성 인식: '
    
        m = 0
        for n in range(len(sub_text_temp)+1):
            if m == len(sub_text_temp) // 27 and len(sub_text_temp) % 27 != 0:
                sub_text += sub_text_temp[len(sub_text_temp) - len(sub_text_temp) % 27:len(sub_text_temp)]
                sub_text += '\n'
                break
            if n > 0 and n % 27 == 0:
                sub_text += sub_text_temp[27*m:27*(m+1)]
                sub_text += '\n'
                m += 1
        
        self.audio_suggestion.setText(volume_suggestion+spm_per_sec_suggestion+'\n')
        self.audio_result.setText(volume_text+spm__per_sec_text+sub_text)
        self.audio_result.update()


    def goto_welcome(self):
        self.controller.setScreen(0)

    def goto_rewatch(self):
        self.controller.setScreen(4)
