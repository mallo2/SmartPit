import logging
from AudioAI import AudioAI
from IRacing import IRacing
from MainPresenter import MainPresenter
from TextAI import TextAI
from UI import UI

if __name__ == "__main__":
    file_handler = logging.FileHandler("app.log", mode='w')
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[
                            logging.FileHandler("app.log"),
                            logging.StreamHandler()
                        ])
    ir = IRacing()
    audio_AI = AudioAI()
    text_AI = TextAI()
    ui = UI()
    MainPresenter(ui, audio_AI, text_AI, ir)