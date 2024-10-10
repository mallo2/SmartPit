import logging
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
        self.__speech_voice = get_key('.env', 'SPEECH_VOICE')
        self.__path_file_record = get_key('.env', 'PATH_FILE_RECORD')
        self.__path_file_response = get_key('.env', 'PATH_FILE_RESPONSE')
        self.__path_file_welcome = get_key('.env', 'PATH_FILE_WELCOME')
        self.__whisper_model_name = get_key('.env', 'WHISPER_MODEL')
        self.__model = whisper.load_model(self.__whisper_model_name)
        logging.info("Audio AI initialized")

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

        def __callback(indata, _frames, _time, _status):
            recording_data.append(indata.copy())

        stream = sd.InputStream(callback=__callback, channels=1, samplerate=sample_rate)
        stream.start()
        return stream

    def play_welcome_sound(self) -> None:
        """
        FR : Méthode permettant de jouer le message de bienvenue\n
        EN : Method to play the welcome message\n
        """
        pygame.mixer.init()
        pygame.mixer.music.load(self.__path_file_welcome)
        pygame.mixer.music.play()

    async def play_audio(self, message: str) -> None:
        """
        FR : Méthode permettant de jouer un message audio\n
        EN : Method to play an audio message\n
        :param message: (str)
            FR : Message à lire
            EN : Message to read
        """
        tts = edge_tts.Communicate(message, voice=self.__speech_voice)
        await tts.save(self.__path_file_response)
        pygame.mixer.init()
        pygame.mixer.music.load(self.__path_file_response)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

    def save_audio(self, recording_data: list, sample_rate=44100) -> None:
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
        wavio.write(self.__path_file_record, audio_array, sample_rate, sampwidth=2)

    def transcribe_audio(self) -> str:
        """
        FR : Méthode permettant de transcrire l'audio en texte\n
        EN : Method to transcribe audio to text\n
        :return: (str)
            FR : Transcription de l'audio
            EN : Audio transcription
        """
        result = self.__model.transcribe(self.__path_file_record)
        return result["text"]
