import asyncio
import os
import sys
import threading
import re
import pygame
from dotenv import get_key

def delete_file_if_exists(filename):
    """
    FR : Méthode permettant de supprimer un fichier s'il existe\n
    EN : Method to delete a file if it exists
    :param filename:
    :return:
    """
    if os.path.exists(filename):
        os.remove(filename)

def get_devices_name() -> list[str]:
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

def change_order_devices(devices) -> None:
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

def get_ordered_devices() -> list[str]:
    devices = get_devices_name()
    change_order_devices(devices)
    return devices

class MainPresenter:
    def __init__(self, ui, audio_AI, text_AI, ir):
        """
        FR : Constructeur de la classe\n
        EN : Constructor of the class
        """
        self.devices = get_ordered_devices()
        self.ui = ui
        self.audio_AI = audio_AI
        self.text_AI = text_AI
        self.ir = ir

        self.ui.set_presenter(self)
        self.ui.mainloop()

    def process(self, try_count: int):
        """
        FR : Méthode permettant de traiter la demande\n
        EN : Method to process the request

        :param try_count:
        :return:
        """
        request = self.audio_AI.transcribe_audio()
        informations_requested = self.text_AI.process_request(request=request)
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
            method = getattr(self.ir, method_name)
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
            return self.process(try_count=try_count)

    def launch_application(self, idx):
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
        self.audio_AI.play_welcome_sound()
        is_recording = False
        recording_data = []
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN and event.button == int(
                        get_key('.env', 'MAIN_BUTTON')) and not is_recording:
                    print("Début de l'enregistrement")
                    delete_file_if_exists(get_key('.env', 'RESPONSE_FILENAME'))
                    recording_data = []
                    stream = self.audio_AI.record_audio(recording_data)
                    is_recording = True
                elif event.type == pygame.JOYBUTTONUP and event.button == int(
                        get_key('.env', 'MAIN_BUTTON')) and is_recording:
                    stream.stop()
                    stream.close()
                    is_recording = False
                    self.audio_AI.save_audio(recording_data)
                    processed = self.process(try_count=0)
                    response = self.text_AI.generate_response(processed["question"], processed["response"])
                    asyncio.run(self.audio_AI.play_audio(response))
                elif event.type == pygame.JOYBUTTONDOWN and event.button == get_key('.env', 'SECOND_BUTTON'):
                    threading.Thread(target=self.ir.thread_fuel_consumption).start()
                pygame.time.wait(100)




