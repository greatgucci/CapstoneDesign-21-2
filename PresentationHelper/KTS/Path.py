import sys
import os

class Path:
    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    @staticmethod
    def path_WelcomeScreen():
        return Path.resource_path("UI/welcome.ui")
    @staticmethod
    def path_RecordScreen():
        return Path.resource_path("UI/record.ui")
    @staticmethod
    def path_AnalyzingScreen():
        return Path.resource_path("UI/analyzing.ui")
    @staticmethod
    def path_VideoAnalyzedScreen():
        return Path.resource_path("UI/video_analyzed.ui")
    @staticmethod
    def path_AudioAnalyzedScreen():
        return Path.resource_path("UI/audio_analyzed.ui")
    @staticmethod
    def path_RewatchScreen():
        return Path.resource_path("UI/rewatch.ui")

    @staticmethod
    def path_VideoOutput():
        return Path.resource_path('Output/video.mp4')
    @staticmethod
    def path_SoundOuput():
        return Path.resource_path('Output/output.wav')
    @staticmethod
    def path_EmotionModel():
        return Path.resource_path('files/emotion_model.hdf5')
    @staticmethod
    def path_Haarcascarde():
        return Path.resource_path('files/haarcascade_frontalface_default.xml')
    def path_SoundDistributedFile(per,i):
        return Path.resource_path("Output/{0}second{1}.wav".format(per, i))
    