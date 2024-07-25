import threading
import pygame
from AudioAI import AudioAI, record_audio, save_audio, play_welcome_sound
import TextAI as TextAI
from IRacing import IRacing
from customtkinter import CTk
from UI import UI
from Device import is_good_device, init_device, get_devices_name


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
                    informations_requested = text_AI.process_request(audioAI=audio_AI)
                    print(informations_requested)
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
