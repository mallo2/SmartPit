import os
import threading
import pygame
import sys
from AudioAI import AudioAI, record_audio, save_audio, play_welcome_sound
import TextAI as TextAI
from IRacing import IRacing
from customtkinter import CTk
from UI import UI


def is_good_wheel(joystick):
    return joystick.get_name() == os.getenv("DEVICE_NAME") and joystick.get_numbuttons() == os.getenv(
        "COUNT_BUTTONS")


def get_joysticks_name():
    names = []
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("Aucun périphérique de jeu connecté.")
        sys.exit()
    for i in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        names.append(joystick.get_name())
    return names


def init_joystick():
    joystick = pygame.joystick.Joystick(pygame.joystick.get_count() - 1)
    joystick.init()
    return joystick


def launch_application():
    play_welcome_sound()
    print("Lancement de l'application")
    ir = IRacing()
    audio_AI = AudioAI()
    text_AI = TextAI.TextAI()
    joystick = init_joystick()
    if is_good_wheel(joystick):
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
                    informations_requested = text_AI.process_request(audioAI=audio_AI)
                    print(informations_requested)
                elif event.type == pygame.JOYBUTTONDOWN and event.button == 21:
                    threading.Thread(target=ir.thread_fuel_consumption).start()

                pygame.time.wait(100)


class SmartPit(CTk):
    def __init__(self):
        super().__init__()
        UI(self, ["Fanatec", "Logitech", "Thrustmaster"])


if __name__ == "__main__":
    sp = SmartPit()
    sp.mainloop()
