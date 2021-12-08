from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from Path import Path

page_max = 1
page = 1
sub_text_temp = ''
sub_text_temp_for_back = []


class AudioAnalyzedScreen(QMainWindow):

    def __init__(self, controller):
        super(AudioAnalyzedScreen, self).__init__()
        loadUi(Path.path_AudioAnalyzedScreen(), self)

        if page == 1:
            self.back_page.hide()
        else:
            self.back_page.show()

        self.controller = controller
        self.add_page.clicked.connect(self.goto_next_page)
        self.back_page.clicked.connect(self.goto_back_page)
        self.to_videoAnalyzed.clicked.connect(self.goto_videoAnalyzed)
        self.to_welcome.clicked.connect(self.goto_welcome)
        self.to_rewatch.clicked.connect(self.goto_rewatch)

    # 화면 넘어왔을때 호출되는 함수
    def onload(self):
        print("AudioAnalyzeSceneLoaded")
        self.print_audio_data(self.controller.sound_analyze_data, self.controller.record_second)

    def back_page_visible(self, back_page):
        if page == 1:
            back_page.hide()
        else:
            back_page.show()

    def add_page_visible(self, add_page):
        if page == page_max and page != 1:
            add_page.hide()
        else:
            add_page.show()

    # 오디오 분석 결과 유저에게 전달하는 함수
    def print_audio_data(self, sound_data, record_seconds):

        global page, sub_text_temp, sub_text_temp_for_back, page_max

        highlight_r = "font: 20pt \"예스 고딕 레귤러\"; Color : red"
        highlight_b = "font: 20pt \"예스 고딕 레귤러\"; Color : skyblue"
        normal = "font: 20pt \"예스 고딕 레귤러\"; Color : white"
        sub_normal = "font: 19pt \"예스 고딕 레귤러\"; Color : white"

        ## 볼륨
        volume_sum = 0.0
        for i in range(len(sound_data[0])):
            volume_sum += round(sound_data[0][i], 1)
        # DURATION 단위 평균
        volume_avg = round(volume_sum / len(sound_data[0]), 1)
        self.audio_result0.setText('볼륨(dB): ' + str(volume_avg) + '\n')
        self.audio_result0.setStyleSheet(normal)

        volume_suggestion = '볼륨: '
        # 53.9~69까지가 적정 범위
        # +-5dB
        if volume_avg <= 43.9:
            volume_suggestion += '훨씬 더 크게 말하시면 좋겠네요'
            self.audio_result0.setStyleSheet(highlight_b)
        elif 43.9 < volume_avg <= 48.9:
            volume_suggestion += '좀 더 크게 말하시면 좋겠네요'
            self.audio_result0.setStyleSheet(highlight_b)
        elif 48.9 < volume_avg < 53.9:
            volume_suggestion += '약간 더 크게 말하시면 좋겠네요'
            self.audio_result0.setStyleSheet(highlight_b)
        elif 69 < volume_avg < 74:
            volume_suggestion += '약간 더 작게 말하시면 좋겠네요'
            self.audio_result0.setStyleSheet(highlight_r)
        elif 74 <= volume_avg < 79:
            volume_suggestion += '좀 더 작게 말하시면 좋겠네요'
            self.audio_result0.setStyleSheet(highlight_r)
        elif 79 <= volume_avg:
            volume_suggestion += '훨씬 더 작게 말하시면 좋겠네요'
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
                sub_text_temp += ' ' + sound_data[1][k]
        

        # 1초 단위 평균
        spm_avg = round(len(sub_text_temp) / record_seconds, 2)
        self.audio_result1.setText('빠르기(초당 음절수): ' + str(spm_avg) + '\n')

        self.audio_result1.setStyleSheet(normal)

        spm_suggestion = '빠르기: '
        # 5.33~6.01까지가 적정 범위
        # +-0.5
        if spm_avg <= 4.33:
            spm_suggestion += '훨씬 더 빠르게 말하시면 좋겠네요'
            self.audio_result1.setStyleSheet(highlight_b)
        elif 4.33 < spm_avg <= 4.83:
            spm_suggestion += '좀 더 빠르게 말하시면 좋겠네요'
            self.audio_result1.setStyleSheet(highlight_b)
        elif 4.83 < spm_avg < 5.33:
            spm_suggestion += '약간 더 빠르게 말하시면 좋겠네요'
            self.audio_result1.setStyleSheet(highlight_b)
        elif 6.01 < spm_avg < 6.51:
            spm_suggestion += '약간 더 느리게 말하시면 좋겠네요'
            self.audio_result1.setStyleSheet(highlight_r)
        elif 6.51 <= spm_avg < 7.01:
            spm_suggestion += '좀 더 느리게 말하시면 좋겠네요'
            self.audio_result1.setStyleSheet(highlight_r)
        elif 7.01 <= spm_avg:
            spm_suggestion += '훨씬 더 느리게 말하시면 좋겠네요'
            self.audio_result1.setStyleSheet(highlight_r)
        else:
            spm_suggestion += '적당합니다'
        spm_suggestion += '\n'

        ## 음성 인식
        sub_text = '음성 인식: '
        sub_text_title = sub_text
        m = 0
        n = 0
        # 500은 페이지 기준
        if len(sub_text_temp) % 500 == 0:
            page_max += len(sub_text_temp) // 500 - 1
            if page_max > 1:
                sub_text_per_page = sub_text_temp[:500]
                sub_text_temp = sub_text_temp[500:]
            else:
                sub_text_per_page = sub_text_temp
        else:
            page_max += len(sub_text_temp) // 500
            if page_max > 1:
                sub_text_per_page = sub_text_temp[:500]
                sub_text_temp = sub_text_temp[500:]
            else:
                sub_text_per_page = sub_text_temp
        # 60는 ui의 width와 매칭되는 글자수
        while True:
            # 첫번째 줄
            if m == 0:
                sub_text += sub_text_per_page[0:60 - len(sub_text_title)] + '\n'
                n += 60 - len(sub_text_title)
                if n == 0:
                    break
            # 마지막 줄
            # and len(sub_text_temp) % 60 != 0
            if m == len(sub_text_per_page) // 60:
                # len(sub_text_temp) - len(sub_text_temp) % 60
                sub_text += sub_text_per_page[n:len(sub_text_per_page)]
                break
            # 그 외
            else:
                sub_text += sub_text_per_page[n:n + 60] + '\n'
                n += 60
            m += 1
        sub_text_temp_for_back.append(sub_text)

        self.audio_result2.setText(sub_text)
        self.audio_result2.setStyleSheet(sub_normal)
        self.audio_suggestion.setText(volume_suggestion + spm_suggestion + '\n')

    def goto_next_page(self):
        global page, sub_text_temp, sub_text_temp_for_back

        sub_normal = "font: 20pt \"예스 고딕 레귤러\"; Color : white"

        n = 0
        m = 0
        sub_text = '음성 인식: '
        sub_text_title = sub_text

        if page_max > 1:
            sub_text_per_page = sub_text_temp[:290]
            sub_text_temp = sub_text_temp[290:]
            # 30은 ui의 width와 매칭되는 글자수
            if page >= 1:

                while True:
                    # 첫번째 줄
                    if m == 0:
                        sub_text += sub_text_per_page[0:30 - len(sub_text_title)] + '\n'
                        n += 30 - len(sub_text_title)
                    # 마지막 줄
                    # and len(sub_text_temp) % 30 != 0
                    elif m == len(sub_text_per_page) // 30:
                        # len(sub_text_temp) - len(sub_text_temp) % 30
                        sub_text += sub_text_per_page[n:len(sub_text_per_page)]
                        break
                    # 그 외
                    else:
                        sub_text += sub_text_per_page[n:n + 30] + '\n'
                        n += 30
                    m += 1
                page += 1

                sub_text_temp_for_back.append(sub_text)
                self.audio_result2.setText(sub_text)
                self.audio_result2.setStyleSheet(sub_normal)
                self.add_page_visible(self.add_page)
                self.back_page_visible(self.back_page)
            else:
                pass

    def goto_back_page(self):
        global page, sub_text_temp_for_back
        sub_normal = "font: 20pt \"예스 고딕 레귤러\"; Color : white"

        if page > 1:
            self.audio_result2.setText(sub_text_temp_for_back[page - 2])
            self.audio_result2.setStyleSheet(sub_normal)
            page -= 1
            self.add_page_visible(self.add_page)
            self.back_page_visible(self.back_page)
        else:
            pass

    def goto_welcome(self):
        self.controller.setScreen(0)

    def goto_rewatch(self):
        self.controller.setScreen(5)

    def goto_videoAnalyzed(self):
        self.controller.setScreen(3)