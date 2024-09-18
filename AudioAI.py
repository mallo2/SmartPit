import pygame
import sounddevice as sd
import wavio
import numpy as np
import whisper
from dotenv import get_key

# FR : Méthode permettant d'écrire le fichier audio sur base de l'enregistrement
# EN :
def save_audio(recording_data, sample_rate=44100):
    audio_array = np.concatenate(recording_data, axis=0)
    wavio.write(get_key('.env', 'FILENAME_RECORD'), audio_array, sample_rate, sampwidth=2)

# FR : Méthode permettant d'enregistrer l'audio
# EN :
def record_audio(recording_data: list, sample_rate=44100):
    def callback(indata, _frames, _time, _status):
        recording_data.append(indata.copy())

    stream = sd.InputStream(callback=callback, channels=1, samplerate=sample_rate)
    stream.start()
    return stream

# FR : Méthode permettant d'exécuter le message de bienvenue
# EN :
def play_welcome_sound():
    pygame.mixer.init()
    pygame.mixer.music.load("ressources/sounds/welcome_message.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


class AudioAI:

    def __init__(self):
        self.model = whisper.load_model(get_key('.env', 'WHISPER_MODEL'))

    # FR : Méthode permettant de transcrire l'audio en texte
    # EN :
    def transcribe_audio(self) -> str:
        audio_file = get_key('.env', 'FILENAME_RECORD')
        result = self.model.transcribe(audio_file)

        return result["text"]
