import logging
import time
import pygame
from functools import partial
from customtkinter import CTkFrame, CTkImage, CTkLabel, CTkEntry, CTkComboBox, CTkButton
from dotenv import set_key, get_key
from customtkinter import CTk
from tkinter import messagebox
from pystray import Icon, MenuItem, Menu
from PIL import Image
import threading


class UI(CTk):
    def __init__(self):
        """
        FR : Constructeur de la classe UI\n
        EN : Constructor of the UI class
        """
        super().__init__()
        threading.Thread(target=self.__setup_tray, daemon=True).start()
        self.__main_button = get_key('.env', 'MAIN_BUTTON')
        self.__second_button = get_key('.env', 'SECOND_BUTTON')
        self.__groq_api_key = get_key('.env', 'GROQ_API_KEY')
        self.__original_devices = None
        self.__devices = None
        self.__presenter = None
        self.__main = self.__init_main(self)
        self.__frame = self.__create_frame()
        self.__create_image()
        self.__textbox = self.__create_textbox()
        self.__dropdown = self.__create_dropdown()
        self.__main_button = self.__create_button_textbox_frame("Assigner la touche principale", self.__main_button)
        self.__second_button = self.__create_button_textbox_frame("Assigner la touche secondaire", self.__second_button)
        self.__create_button()
        self.__alert = self.__create_alert()
        logging.info("UI initialized")

    @staticmethod
    def __init_main(mainWindow):
        """
        FR : Méthode permettant d'initialiser la fenêtre principale\n
        EN : Method to initialize the main window
        :param mainWindow:
            FR : Fenêtre principale
            EN : Main window
        :return:
            FR : Fenêtre principale initialisée
            EN : Initialized main
        """
        mainWindow.title("SmartPit")
        mainWindow.geometry("800x600")
        mainWindow.resizable(False, False)
        mainWindow.iconbitmap('ressources/images/favicon.ico')
        return mainWindow

    @staticmethod
    def __update_env_file(api_key: str, selected_device: str, main_button: str, second_button: str) -> None:
        """
        FR : Méthode privée permettant de mettre à jour le fichier .env après la validation de la pague d'acceuil\n
        EN : Private method to update the .env file after the validation of the home page
        :param api_key: (str)
            FR : Clé d'API de Groq
            EN : Groq API key
        :param selected_device: (str)
            FR : Périphérique de jeu sélectionné
            EN : Selected game device
        :param main_button: (str)
            FR : Touche principale
            EN : Main button
        :param second_button: (str)
            FR : Touche secondaire
            EN : Second button
        """
        set_key('.env', 'GROQ_API_KEY', api_key)
        set_key('.env', 'SELECTED_DEVICE', selected_device)
        set_key('.env', 'MAIN_BUTTON', main_button)
        set_key('.env', 'SECOND_BUTTON', second_button)

    def __init_textbox(self, textbox: CTkEntry) -> None:
        """
        FR : Méthode permettant d'initialiser le textbox pour la clé d'API de Groq\n
        EN : Method to initialize the textbox for the Groq API key
        :param textbox: (CTkEntry)
            FR : Textbox pour la clé d'API de Groq
            EN : Textbox for the Groq API key
        """
        if self.__groq_api_key and self.__groq_api_key != "":
            textbox.insert(0, self.__groq_api_key)

    def __set_dropdown(self, devices: list[str]) -> None:
        """
        FR : Méthode privée afin d'établir la liste déroulante des périphériques
        EN : Private method to set the dropdown list of devices
        :param devices: (list[str])
            FR : Liste des périphériques
            EN : List of devices
        """
        self.__dropdown.configure(values=devices)
        self.__dropdown.set(devices[0])

    def __get_idx_device_selected(self) -> int:
        """
        FR : Méthode privée permettant de récupérer l'index du périphérique sélectionné\n
        EN : Private method to get the index of the selected device
        :return: (int)
            FR : Index du périphérique sélectionné
            EN : Index of the selected device
        """
        self.__dropdown.configure(state="disabled")
        return self.__original_devices.index(self.__dropdown.get())

    def __clicked(self) -> None:
        """
        FR : Méthode privée appelée lors du clic sur le bouton de démarrage\n
        EN : Private method called when clicking on the start button
        """
        if self.__is_valid_form():
            self.__update_env_file(self.__textbox.get(), self.__dropdown.get(), self.__main_button.get(),
                                   self.__second_button.get())
            logging.info("Environment file updated")
            idx = self.__get_idx_device_selected()
            self.__main.destroy()
            logging.info("Main window destroyed")
            self.__presenter.launch_application(idx)

    def __create_frame(self) -> CTkFrame:
        """
        FR : Méthode privée permettant de créer un frame\n
        EN : Private method to create a frame
        :return:
            FR : Frame créé pour la page d'accueil
            EN : Frame created for the home page
        """
        frame = CTkFrame(master=self.__main, fg_color="#001a35")
        frame.pack(pady=10, padx=30, fill="both", expand=True)
        return frame

    def __create_image(self) -> None:
        """
        FR : Méthode privée permettant de créer l'image du logo\n
        EN : Private method to create the logo image
        """
        logo = CTkImage(light_image=Image.open('ressources/images/logo.jpg'),
                        dark_image=Image.open('ressources/images/logo.jpg'), size=(150, 150))
        title = CTkLabel(master=self.__frame, text="", image=logo)
        title.pack(pady=12, padx=10)

    def __create_textbox(self) -> CTkEntry:
        """
        FR : Méthode privée permettant de créer le textbox pour la clé d'API de Groq\n
        EN : Private method to create the textbox for the Groq API key
        :return: (CTkEntry)
            FR : Textbox créé pour la clé d'API de Groq
            EN : Textbox created for the Groq API key
        """
        textbox = CTkEntry(self.__frame, placeholder_text="GROQ API Key", height=25, width=250, border_width=1,
                           border_color="white")
        textbox.pack(pady=20)
        self.__init_textbox(textbox)
        return textbox

    def __create_dropdown(self) -> CTkComboBox:
        """
        FR : Méthode privée permettant de créer le dropdown pour la sélection du périphérique\n
        EN : Private method to create the dropdown for the device selection
        :return: (CTkComboBox)
            FR : Dropdown créé pour la sélection du périphérique
            EN : Dropdown created for the device selection
        """
        dropdown = CTkComboBox(self.__frame, state="readonly", width=300)
        dropdown.pack(pady=20)
        return dropdown

    def __create_button_textbox_frame(self, text: str, env_key: str) -> CTkEntry:
        """
        FR : Méthode privée permettant de créer un frame avec un textbox et un bouton pour l'assignation de touche\n
        EN : Private method to create a frame with a textbox and a button for key assignment
        :param text: (str)
            FR : Texte du bouton
            EN : Button text
        :param env_key: (str)
            FR : Clé de l'environnement
            EN : Environment key
        :return: (CTkEntry)
            FR : Textbox créé pour l'assignation de touche
            EN : Textbox created for key assignment
        """
        frame = CTkFrame(master=self.__frame, fg_color="#001a35")
        frame.pack(pady=5)
        capture_textbox = CTkEntry(frame, height=30, width=50)
        capture_textbox.pack(side="left")
        capture_textbox.insert(0, env_key)
        button = CTkButton(frame, text=text, command=partial(self.__detect_key, capture_textbox))
        capture_textbox.configure(state="readonly")
        button.pack(side="left", padx=5)
        return capture_textbox

    def __create_button(self) -> None:
        """
        FR : Méthode privée permettant de créer le bouton de démarrage et de validation du formulaire\n
        EN : Private method to create the start button and validate the form
        :return:
            FR : Bouton créé pour la validation du formulaire
            EN : Button created to validate the form
        """
        button = CTkButton(master=self.__frame, text="Démarrer", command=self.__clicked, fg_color="#001a35",
                           border_color="white", border_width=1)
        button.pack(pady=25)

    def __create_alert(self) -> list[CTkLabel]:
        """
        FR : Méthode privée permettant de créer les alertes\n
        EN : Private method to create alerts
        :return: (list[CTkLabel])
            FR : Alertes créées
            EN : Alerts created
        """
        return [CTkLabel(master=self.__frame, text="Veuillez entrer une clé API", fg_color="red", corner_radius=5),
                CTkLabel(master=self.__frame, text="Veuillez assigner une touche principale", fg_color="red",
                         corner_radius=5),
                CTkLabel(master=self.__frame, text="Veuillez assigner une touche secondaire", fg_color="red",
                         corner_radius=5)]

    def __is_valid_form(self) -> bool:
        """
        FR : Méthode privée permettant de valider le formulaire\n
        EN : Private method to validate the form
        :return: (bool)
            FR : True si le formulaire est valide, False sinon
            EN : True if the form is valid, False otherwise
        """
        valid = True
        if self.__textbox.get() == "":
            self.__alert[0].pack(pady=2)
            valid = False
        if self.__main_button.get() == "":
            self.__alert[1].pack(pady=2)
            valid = False
        if self.__second_button.get() == "":
            self.__alert[2].pack(pady=2)
            valid = False
        return valid

    def __detect_key(self, capture_textbox: CTkEntry) -> None:
        """
        FR : Méthode privée permettant de détecter la touche appuyée\n
        EN : Private method to detect the pressed key
        :param capture_textbox: (CTkEntry)
            FR : Textbox pour l'affichage de la touche
            EN : Textbox for displaying the key
        """
        self.__dropdown.configure(state="disabled")
        start_time = time.time()
        joystick = pygame.joystick.Joystick(self.__get_idx_device_selected())
        joystick.init()
        while True:
            if time.time() - start_time > 7.5:
                break
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    capture_textbox.configure(state="normal")
                    capture_textbox.delete(0, "end")
                    capture_textbox.insert(0, f"{event.button}")
                    capture_textbox.configure(state="readonly")
                    return
            pygame.time.wait(100)
        self.__dropdown.configure(state="normal")

    def set_presenter(self, presenter) -> None:
        """
        FR : Méthode permettant de définir la classe presenter \n
        EN : Method to set the presenter
        :param presenter: (MainPresenter)
            FR : Classe presenter
            EN : Presenter class
        """
        self.__presenter = presenter
        self.__devices, self.__original_devices = presenter.devices
        self.__set_dropdown(self.__devices)

    @staticmethod
    def show_error_shutdown(error: str) -> None:
        """
        FR : Méthode statique permettant d'afficher une erreur\n
        EN : Static method to display an error
        :param error: (str)
            FR : Erreur à afficher
            EN : Error to display
        """
        logging.critical(error)
        messagebox.showerror("Erreur d'exécution", error)

    def __quit_app(self, icon) -> None:
        """
        FR : Méthode permettant de quitter l'application\n
        EN :  method to quit the application
        :param icon: (Icon)
            FR : Icône de l'application
            EN : Application icon
        """
        icon.stop()
        logging.info("Application stopped")
        self.__presenter.stop_application(None)

    def __setup_tray(self) -> None:
        """
        FR : Méthode permettant de configurer le systray\n
        EN : Method to configure the systray
        """
        icon_image = Image.open("ressources/images/favicon.ico")

        menu = Menu(
            MenuItem('Quitter', self.__quit_app)
        )

        # Créer l'icône dans la systray
        icon = Icon("SmartPit", icon_image, "SmartPit", menu)
        icon.run()
