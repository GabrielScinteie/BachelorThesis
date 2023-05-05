import threading
import pyttsx3
from PyQt5.QtWidgets import QPushButton
import loadData


class SoundButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

    def enterEvent(self, event):
        if loadData.soundOn:
            t = threading.Thread(target=self.read_text)
            t.start()

    def read_text(self):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(self.text())
            engine.runAndWait()
        except:
            pass