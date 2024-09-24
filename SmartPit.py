from AudioAI import AudioAI
from IRacing import IRacing
from MainPresenter import MainPresenter
from TextAI import TextAI
from UI import UI

if __name__ == "__main__":
    ir = IRacing()
    audio_AI = AudioAI()
    text_AI = TextAI()
    ui = UI()
    MainPresenter(ui, audio_AI, text_AI, ir)