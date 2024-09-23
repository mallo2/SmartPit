import time
import edge_tts
import pygame
import sounddevice as sd
import wavio
import numpy as np
import whisper
from dotenv import get_key

class AudioAI:
    """
    FR : Classe de l'IA audio\n
    EN : Audio AI class
    """
    def __init__(self):
        """
        FR : Constructeur de la classe AudioAI\n
        EN : Constructor of the AudioAI
        """
        self.model = whisper.load_model(get_key('.env', 'WHISPER_MODEL'))
    @staticmethod
    def save_audio(recording_data, sample_rate=44100) -> None:
        """
        FR : Méthode permettant d'écrire le fichier audio sur base de l'enregistrement\n
        EN : Method to write the audio file based on the recording\n
        :param recording_data: (list)
            FR : Données de l'enregistrement
            EN : Recording data
        :param sample_rate: (int)
            FR : Fréquence d'échantillonnage
            EN : Sampling frequency
        """
        audio_array = np.concatenate(recording_data, axis=0)
        wavio.write(get_key('.env', 'FILENAME_RECORD'), audio_array, sample_rate, sampwidth=2)
    @staticmethod
    def record_audio(recording_data: list, sample_rate=44100) -> sd.InputStream:
        """
        FR : Méthode permettant d'enregistrer l'audio\n
        EN : Method to record audio\n
        :param recording_data: (list)
            FR : Données de l'enregistrement
            EN : Recording data
        :param sample_rate: (int)
            FR : Fréquence d'échantillonnage
            EN : Sampling frequency
        :return: (sd.InputStream)
            FR : Stream d'entrée
            EN : Input stream
        """
        def callback(indata, _frames, _time, _status):
            recording_data.append(indata.copy())
        stream = sd.InputStream(callback=callback, channels=1, samplerate=sample_rate)
        stream.start()
        return stream
    @staticmethod
    def play_welcome_sound() -> None:
        """
        FR : Méthode permettant de jouer le message de bienvenue\n
        EN : Method to play the welcome message\n
        """
        pygame.mixer.init()
        pygame.mixer.music.load("ressources/sounds/welcome_message.mp3")
        pygame.mixer.music.play()
    @staticmethod
    async def play_audio(message) -> None:
        """
        FR : Méthode permettant de jouer un message audio\n
        EN : Method to play an audio message\n
        :param message: (str)
            FR : Message à lire
            EN : Message to read
        """
        tts = edge_tts.Communicate(message, voice=get_key('.env', 'SPEECH_VOICE'))
        await tts.save(get_key('.env', 'RESPONSE_FILENAME'))
        pygame.mixer.init()
        pygame.mixer.music.load(get_key('.env', 'RESPONSE_FILENAME'))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    def transcribe_audio(self) -> str:
        """
        FR : Méthode permettant de transcrire l'audio en texte\n
        EN : Method to transcribe audio to text\n
        :return: (str)
            FR : Transcription de l'audio
            EN : Audio transcription
        """
        audio_file = get_key('.env', 'FILENAME_RECORD')
        result = self.model.transcribe(audio_file)
        return result["text"]