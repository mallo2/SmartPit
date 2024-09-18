import asyncio
import os
import time

import edge_tts
import pygame
import sounddevice as sd
import wavio
import numpy as np
import whisper
from dotenv import get_key


def save_audio(recording_data, sample_rate=44100):
    """
    FR : Méthode permettant d'écrire le fichier audio sur base de l'enregistrement\n
    EN :
    :param recording_data:
    :param sample_rate:
    :return:
    """
    audio_array = np.concatenate(recording_data, axis=0)
    wavio.write(get_key('.env', 'FILENAME_RECORD'), audio_array, sample_rate, sampwidth=2)


def record_audio(recording_data: list, sample_rate=44100):
    """
    FR : Méthode permettant d'enregistrer l'audio\n
    EN :
    :param recording_data:
    :param sample_rate:
    :return:
    """

    def callback(indata, _frames, _time, _status):
        recording_data.append(indata.copy())

    stream = sd.InputStream(callback=callback, channels=1, samplerate=sample_rate)
    stream.start()
    return stream


def play_welcome_sound():
    """
    FR : Méthode permettant de jouer le message de bienvenue\n
    EN :
    :return:
    """
    pygame.mixer.init()
    pygame.mixer.music.load("ressources/sounds/welcome_message.mp3")
    pygame.mixer.music.play()


async def play_audio(message):
    """
    FR : Méthode permettant de jouer un message audio\n
    EN : Method to play an audio message\n
    :param message:
    :return:
    """
    tts = edge_tts.Communicate(message, voice="fr-FR-VivienneMultilingualNeural")
    await tts.save(get_key('.env', 'RESPONSE_FILENAME'))
    pygame.mixer.init()
    pygame.mixer.music.load(get_key('.env', 'RESPONSE_FILENAME'))
    pygame.mixer.music.play()

    # Wait until the audio finishes playing
    while pygame.mixer.music.get_busy():
        time.sleep(1)

    # Stop, unload, and delete the file
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()



class AudioAI:

    def __init__(self):
        self.model = whisper.load_model(get_key('.env', 'WHISPER_MODEL'))

    def transcribe_audio(self) -> str:
        """
        FR : Méthode permettant de transcrire l'audio en texte\n
        EN :
        :return:
        """
        audio_file = get_key('.env', 'FILENAME_RECORD')
        result = self.model.transcribe(audio_file)
        return result["text"]
