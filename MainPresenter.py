import asyncio
import logging
import os
import signal
import sys
import threading
import re
import pygame
from dotenv import get_key
from AudioAI import AudioAI
from IRacing import IRacing
from TextAI import TextAI
from UI import UI


class MainPresenter:
    def __init__(self, ui: UI, audio_AI: AudioAI, text_AI: TextAI, ir: IRacing):
        """
        FR : Constructeur de la classe MainPresenter\n
        EN : Constructor of the MainPresenter class
        :param ui:  (UI)
            FR : Interface utilisateur\n
            EN : User interface
        :param audio_AI: (AudioAI)
            FR : Intelligence artificielle audio\n
            EN : Audio artificial intelligence
        :param text_AI: (TextAI)
            FR : Intelligence artificielle textuelle\n
            EN : Textual artificial intelligence
        :param ir: (IRacing)
            FR : Objet permettant de communiquer avec iRacing\n
            EN : Object allowing to communicate with iRacing
        """
        self.__lock_file = "smartpit.lock"
        self.devices = self.__get_ordered_devices()
        self.__ui = ui
        self.__ui.protocol("WM_DELETE_WINDOW", lambda: self.__stop_application(None))
        self.__create_lock_file()
        self.__audio_AI = audio_AI
        self.__text_AI = text_AI
        self.__ir = ir
        self.__ui.set_presenter(self)
        logging.info("MainPresenter initialized")
        self.__ui.mainloop()

    @staticmethod
    def __delete_file_if_exists(filename: str) -> None:
        """
        FR : Méthode permettant de supprimer un fichier s'il existe\n
        EN : Method to delete a file if it exists
        :param filename:
            FR : Nom du fichier\n
            EN : Name of the file
        """
        if os.path.exists(filename):
            os.remove(filename)

    @staticmethod
    def __get_devices_name() -> list[str]:
        """
        FR : Méthode permettant de récupérer les noms des périphériques de jeu\n
        EN : Method to get the names of the game devices
        :return:
            FR : Liste contenant les noms des périphériques de jeu\n
            EN : List containing the names of the game devices
        """
        names = []
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            logging.critical("No game device connected")
            raise Exception("No game device connected")
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            names.append(f"{joystick.get_name()} ({joystick.get_numbuttons()})")
        return names

    @staticmethod
    def __change_order_devices(devices: list[str]) -> None:
        """
        FR : Méthode permettant de changer l'ordre des devices en placant le périphérique sélectionné en premier\n
        EN : Method to change the order of the devices by placing the selected device first
        :param devices: (list[str])
            FR : Liste des périphériques de jeu\n
            EN : List of game devices
        """
        selected_device = get_key('.env', 'SELECTED_DEVICE')
        if selected_device and selected_device != "" and selected_device in devices:
            devices.remove(selected_device)
            devices.insert(0, selected_device)

    def __stop_application(self, error) -> None:
        """
        FR : Méthode permettant d'arrêter l'application\n
        EN : Method to stop the application
        :param error: (str)
            FR : Message d'erreur\n
            EN : Error message
        """
        if error:
            self.__ui.show_error_shutdown(error)
        self.__delete_file_if_exists(self.__lock_file)
        sys.exit()

    def __create_lock_file(self) -> None:
        """
        FR : Méthode permettant de créer un fichier de verrouillage\n
        EN : Method to create a lock file
        """
        if os.path.exists(self.__lock_file):
            self.__stop_application("Application already running")
        else:
            with open(self.__lock_file, 'w') as lock_file:
                lock_file.write(str(os.getpid()))

    def __get_ordered_devices(self) -> tuple[list[str], list[str]]:
        """
        FR : Méthode permettant de récupérer les périphériques de jeu ordonnés\n
        EN : Method to get the ordered game devices
        :return:
            FR : Tuple contenant les périphériques de jeu ordonnés et les périphériques de jeu originaux\n
            EN : Tuple containing the ordered game devices and the original game devices
        """
        devices = self.__get_devices_name()
        original_devices = devices.copy()
        self.__change_order_devices(devices)
        return devices, original_devices

    def __process(self, try_count: int) -> dict:
        """
        FR : Méthode permettant de traiter la demande\n
        EN : Method to process the request
        :param try_count: (int)
            FR : Nombre de tentatives\n
            EN : Number of attempts
        :return:
            FR : Dictionnaire contenant la question et la réponse\n
            EN : Dictionary containing the question and the answer
        """
        request = self.__audio_AI.transcribe_audio()
        informations_requested = self.__text_AI.process_request(request=request)
        question = informations_requested["audio_text"]
        function = informations_requested["response"]
        logging.info(f"Question : {question}")
        logging.info(f"Fonction : {function}")
        match = re.match(r"(\w+)\((.*)\)", function)

        if try_count >= 3:
            self.__delete_file_if_exists(get_key('.env', 'PATH_FILE_RECORD'))
            return {
                "question": question,
                "response": "Je n'ai pas compris votre demande"
            }

        if match:
            method_name = match.group(1)
            args = match.group(2)
            method = getattr(self.__ir, method_name)
            if args == "" or args is None:
                data_result = method()
                logging.info(f"Data : {data_result}")
                if data_result is None:
                    data_result = "Commande exécutée avec succès"
                self.__delete_file_if_exists(get_key('.env', 'PATH_FILE_RECORD'))
                return {
                    "question": question,
                    "response": data_result
                }

            arg_values = [eval(arg.strip()) for arg in args.split(',')]
            data_result = method(*arg_values)
            self.__delete_file_if_exists(get_key('.env', 'PATH_FILE_RECORD'))
            return {
                "question": question,
                "response": data_result
            }

        else:
            try_count += 1
            logging.warning("Invalid string format")
            return self.__process(try_count=try_count)

    def launch_application(self, idx):
        """
            FR : Méthode permettant de lancer l'application\n
            EN : Method to launch the application
            :param idx: (int)
                FR : Index du périphérique de jeu\n
                EN : Index of the game device
            """
        logging.info("Application launched")
        try:
            pygame.init()
            pygame.joystick.init()
            joystick = pygame.joystick.Joystick(idx)
            joystick.init()
            self.__ir.connect()
            self.__audio_AI.play_welcome_sound()
            logging.info("Application connected to iRacing")
            is_recording = False
            recording_data = []
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.JOYBUTTONDOWN and event.button == int(
                            get_key('.env', 'MAIN_BUTTON')) and not is_recording:
                        logging.info("Recording started")
                        self.__delete_file_if_exists(get_key('.env', 'PATH_FILE_RESPONSE'))
                        recording_data = []
                        stream = self.__audio_AI.record_audio(recording_data)
                        is_recording = True
                    elif event.type == pygame.JOYBUTTONUP and event.button == int(
                            get_key('.env', 'MAIN_BUTTON')) and is_recording:
                        logging.info("Recording stopped")
                        stream.stop()
                        stream.close()
                        is_recording = False
                        self.__audio_AI.save_audio(recording_data)
                        logging.info("Audio saved")
                        processed = self.__process(try_count=0)
                        logging.info(f"Question : {processed['question']}")
                        logging.info(f"Réponse : {processed['response']}")
                        response = self.__text_AI.generate_response(processed["question"], processed["response"])
                        logging.info(f"Réponse IA : {response}")
                        asyncio.run(self.__audio_AI.play_audio(response))
                        logging.info("Audio played")
                    elif event.type == pygame.JOYBUTTONDOWN and event.button == get_key('.env', 'SECOND_BUTTON'):
                        threading.Thread(target=self.__ir.thread_fuel_consumption).start()

                    pygame.time.wait(10)
        except Exception as e:
            self.__stop_application(str(e))
