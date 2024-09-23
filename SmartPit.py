import asyncio
import os
import sys
import threading
import re
import pygame
from dotenv import get_key
from AudioAI import AudioAI
from TextAI import TextAI
from IRacing import IRacing
from customtkinter import CTk
from UI import UI

def change_order_devices(devices):
    """
    FR : Méthode permettant de changer l'ordre des devices en placant le périphérique sélectionné en premier\n
    EN : Method to change the order of the devices by placing the selected device first
    :param devices:
    :return:
    """
    selected_device = get_key('.env', 'SELECTED_DEVICE')
    if selected_device and selected_device != "" and selected_device in devices:
        devices.remove(selected_device)
        devices.insert(0, selected_device)

def delete_file_if_exists(filename):
    """
    FR : Méthode permettant de supprimer un fichier s'il existe\n
    EN : Method to delete a file if it exists
    :param filename:
    :return:
    """
    if os.path.exists(filename):
        os.remove(filename)


def get_devices_name():
    """
    FR : Méthode permettant de récupérer les noms des périphériques de jeu\n
    EN : Method to get the names of the game devices
    :return:
    """
    names = []
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("Aucun périphérique de jeu connecté.")
        sys.exit()
    for i in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        names.append(f"{joystick.get_name()} ({joystick.get_numbuttons()})")
    return names


def process(text_AI: TextAI, audio_AI: AudioAI, ir: IRacing, try_count: int):
    """
    FR : Méthode permettant de traiter la demande\n
    EN : Method to process the request
    :param text_AI:
    :param audio_AI:
    :param ir:
    :param try_count:
    :return:
    """
    request = audio_AI.transcribe_audio()
    informations_requested = text_AI.process_request(request=request)
    question = informations_requested["audio_text"]
    function = informations_requested["response"]
    match = re.match(r"(\w+)\((.*)\)", function)
    if try_count >= 3:
        delete_file_if_exists(get_key('.env', 'FILENAME_RECORD'))
        return {
            "question": question,
            "response": "Je n'ai pas compris votre demande"
        }
    if match:
        method_name = match.group(1)
        args = match.group(2)
        method = getattr(ir, method_name)
        if args == "" or args is None:
            # TODO: Gérer l exception si la méthode bug
            data_result = method()
            delete_file_if_exists(get_key('.env', 'FILENAME_RECORD'))
            return {
                "question": question,
                "response": data_result
            }
        arg_values = [eval(arg.strip()) for arg in args.split(',')]
        data_result = method(*arg_values)
        delete_file_if_exists(get_key('.env', 'FILENAME_RECORD'))
        return {
            "question": question,
            "response": data_result
        }
    else:
        try_count += 1
        print("Format de chaîne invalide")
        return process(text_AI=text_AI, audio_AI=audio_AI, ir=ir, try_count=try_count)


def launch_application(idx):
    """
    FR : Méthode permettant de lancer l'application\n
    EN : Method to launch the application
    :param idx:
    :return:
    """
    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(idx)
    joystick.init()
    ir = IRacing()
    audio_AI = AudioAI()
    text_AI = TextAI()
    audio_AI.play_welcome_sound()
    is_recording = False
    recording_data = []
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN and event.button == int(
                    get_key('.env', 'MAIN_BUTTON')) and not is_recording:
                print("Début de l'enregistrement")
                delete_file_if_exists(get_key('.env', 'RESPONSE_FILENAME'))
                recording_data = []
                stream = audio_AI.record_audio(recording_data)
                is_recording = True
            elif event.type == pygame.JOYBUTTONUP and event.button == int(
                    get_key('.env', 'MAIN_BUTTON')) and is_recording:
                stream.stop()
                stream.close()
                is_recording = False
                audio_AI.save_audio(recording_data)
                processed = process(text_AI=text_AI, audio_AI=audio_AI, ir=ir, try_count=0)
                response = text_AI.generate_response(processed["question"], processed["response"])
                asyncio.run(audio_AI.play_audio(response))
            elif event.type == pygame.JOYBUTTONDOWN and event.button == get_key('.env', 'SECOND_BUTTON'):
                threading.Thread(target=ir.thread_fuel_consumption).start()

            pygame.time.wait(100)


class SmartPit(CTk):
    def __init__(self):
        """
        FR : Constructeur de la classe\n
        EN : Constructor of the class
        """
        super().__init__()
        devices = get_devices_name()
        change_order_devices(devices)
        UI(self, devices)


if __name__ == "__main__":
    sp = SmartPit()
    sp.mainloop()
