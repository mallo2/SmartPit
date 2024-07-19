import os
import sounddevice as sd
import wavio
import numpy as np
import whisper


def delete_file_if_exists(filename):
    if os.path.exists(filename):
        os.remove(filename)


def save_audio(recording_data, sample_rate=44100):
    audio_array = np.concatenate(recording_data, axis=0)
    wavio.write(os.getenv("FILENAME_RECORD"), audio_array, sample_rate, sampwidth=2)


def record_audio(recording_data: list, sample_rate=44100):
    def callback(indata, _frames, _time, _status):
        recording_data.append(indata.copy())

    stream = sd.InputStream(callback=callback, channels=1, samplerate=sample_rate)
    stream.start()
    return stream


class AudioAI:

    def __init__(self):
        self.model = whisper.load_model(os.getenv("WHISPER_MODEL"))

    def transcribe_audio(self) -> str:
        audio_file = os.getenv("FILENAME_RECORD")
        result = self.model.transcribe(audio_file)
        delete_file_if_exists(os.getenv("FILENAME_RECORD"))
        return result["text"]
