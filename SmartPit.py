import os
import threading
import re
import pygame
from dotenv import get_key
from AudioAI import AudioAI, record_audio, save_audio, play_welcome_sound
import TextAI as TextAI
from IRacing import IRacing
from customtkinter import CTk
from UI import UI
from Device import is_good_device, init_device, get_devices_name


def delete_file_if_exists(filename):
    if os.path.exists(filename):
        os.remove(filename)


def process(text_AI: TextAI.TextAI, audio_AI: AudioAI, ir: IRacing):
    informations_requested = text_AI.process_request(audioAI=audio_AI)
    match = re.match(r"(\w+)\((.*)\)", informations_requested)
    if match:
        method_name = match.group(1)
        args = match.group(2)
        arg_values = [eval(arg.strip()) for arg in args.split(',')]
        method = getattr(ir, method_name)
        data_result = method(*arg_values)
        delete_file_if_exists(get_key('.env', 'FILENAME_RECORD'))
        return data_result
    else:
        print("Format de chaîne invalide")
        process(text_AI=text_AI, audio_AI=audio_AI, ir=ir)


def launch_application():
    play_welcome_sound()
    ir = IRacing()
    audio_AI = AudioAI()
    text_AI = TextAI.TextAI()
    joystick = init_device()
    if is_good_device(joystick):
        is_recording = False
        recording_data = []

        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN and event.button == 1 and not is_recording:
                    print("Début de l'enregistrement")
                    recording_data = []
                    stream = record_audio(recording_data)
                    is_recording = True
                elif event.type == pygame.JOYBUTTONUP and event.button == 1 and is_recording:
                    stream.stop()
                    stream.close()
                    is_recording = False
                    save_audio(recording_data)
                    data_result = process(text_AI=text_AI, audio_AI=audio_AI, ir=ir)
                    print(data_result)
                elif event.type == pygame.JOYBUTTONDOWN and event.button == 21:
                    threading.Thread(target=ir.thread_fuel_consumption).start()

                pygame.time.wait(100)


class SmartPit(CTk):
    def __init__(self):
        super().__init__()
        UI(self, get_devices_name())


if __name__ == "__main__":
    sp = SmartPit()
    sp.mainloop()
