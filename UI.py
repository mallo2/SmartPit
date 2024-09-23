import time
import pygame
from functools import partial
from PIL import Image
from customtkinter import CTkFrame, CTkImage, CTkLabel, CTkEntry, CTkComboBox, CTkButton
from dotenv import set_key, get_key


class UI:
    def __init__(self, smartPit, devices: list[str]):
        """
        FR : Constructeur de la classe UI\n
        EN : Constructor of the UI class
        :param smartPit:
            FR :
            EN :
        :param devices:
            FR :
            EN :
        """
        self.devices = devices
        self.main = self.init_main(smartPit)
        self.frame = self.create_frame()
        self.create_image()
        self.textbox = self.create_textbox()
        self.dropdown = self.create_dropdown(devices)
        self.main_button = self.create_button_textbox_frame("Assigner la touche principale", get_key('.env', 'MAIN_BUTTON'))
        self.second_button = self.create_button_textbox_frame("Assigner la touche secondaire", get_key('.env', 'SECOND_BUTTON'))
        self.create_button()
        self.alert = self.create_alert()

    @staticmethod
    def init_main(smartPit):
        """
        FR : Méthode permettant d'initialiser la fenêtre principale\n
        EN : Method to initialize the main window
        :param smartPit:
        :return:
        """
        smartPit.title("SmartPit")
        smartPit.geometry("800x600")
        smartPit.resizable(False, False)
        smartPit.iconbitmap('ressources/images/favicon.ico')
        return smartPit

    @staticmethod
    def init_textbox(textbox) -> None:
        """
        FR : Méthode permettant d'initialiser le textbox pour la clé d'API de Groq\n
        EN : Method to initialize the textbox for the Groq API key
        :param textbox:
            FR :
            EN :
        """
        groq_api_key = get_key('.env', 'GROQ_API_KEY')
        if groq_api_key and groq_api_key != "":
            textbox.insert(0, groq_api_key)

    @staticmethod
    def update_env_file(api_key, selected_device, main_button, second_button):
        """
        FR : Méthode permettant de mettre à jour le fichier .env après la validation de la pague d'acceuil\n
        EN : Method to update the .env file after the validation of the home page
        :param api_key:
        :param selected_device:
        :param main_button:
        :param second_button:
        :return:
        """
        set_key('.env', 'GROQ_API_KEY', api_key)
        set_key('.env', 'SELECTED_DEVICE', selected_device)
        set_key('.env', 'MAIN_BUTTON', main_button)
        set_key('.env', 'SECOND_BUTTON', second_button)

    def clicked(self) -> None:
        """
        FR : Méthode appelée lors du clic sur le bouton de démarrage\n
        EN : Method called when clicking on the start button
        """
        from SmartPit import launch_application
        if self.is_valid_form():
            self.update_env_file(self.textbox.get(), self.dropdown.get(), self.main_button.get(), self.second_button.get())
            idx = self.devices.index(self.dropdown.get())
            self.main.destroy()
            launch_application(idx)

    def create_frame(self):
        """
        FR : Méthode permettant de créer un frame\n
        EN : Method to create a frame
        :return:
            FR :
            EN :
        """
        frame = CTkFrame(master=self.main, fg_color="#001a35")
        frame.pack(pady=10, padx=30, fill="both", expand=True)
        return frame

    def create_image(self) -> None:
        """
        FR : Méthode permettant de créer l'image du logo\n
        EN : Method to create the logo image
        """
        logo = CTkImage(light_image=Image.open('ressources/images/logo.jpg'),
                        dark_image=Image.open('ressources/images/logo.jpg'), size=(150, 150))
        title = CTkLabel(master=self.frame, text="", image=logo)
        title.pack(pady=12, padx=10)

    def create_textbox(self) -> CTkEntry:
        """
        FR : Méthode permettant de créer le textbox pour la clé d'API de Groq\n
        EN : Method to create the textbox for the Groq API key
        :return:
            FR :
            EN :
        """
        textbox = CTkEntry(self.frame, placeholder_text="GROQ API Key", height=25, width=250, border_width=1,
                           border_color="white")
        textbox.pack(pady=20)
        self.init_textbox(textbox)
        return textbox

    def create_dropdown(self, devices: list[str]):
        """
        FR : Méthode permettant de créer le dropdown pour la sélection du périphérique\n
        EN : Method to create the dropdown for the device selection
        :param devices:
            FR :
            EN :
        :return:
            FR :
            EN :
        """
        dropdown = CTkComboBox(self.frame, values=devices, state="readonly", width=300)
        dropdown.set(devices[0])
        dropdown.pack(pady=20)
        return dropdown

    def create_button_textbox_frame(self, text, env_key):
        # TODO : Finir documentation
        """
        FR : Méthode permettant de créer un frame avec un textbox et un bouton pour l'assignation de touche\n
        EN : Method to create a frame with a textbox and a button for key assignment
        :param text:
        :param env_key:
        :return:
        """
        frame = CTkFrame(master=self.frame, fg_color="#001a35")
        frame.pack(pady=5)
        capture_textbox = CTkEntry(frame, height=30, width=50)
        capture_textbox.pack(side="left")

        capture_textbox.insert(0, env_key)
        button = CTkButton(frame, text=text, command=partial(self.detect_key, capture_textbox))

        capture_textbox.configure(state="readonly")
        button.pack(side="left", padx=5)

        return capture_textbox

    def create_button(self) -> None:
        """
        FR : Méthode permettant de créer le bouton de démarrage et de validation du formulaire\n
        EN : Method to create the start button and validate the form
        :return:
            FR :
            EN :
        """
        button = CTkButton(master=self.frame, text="Démarrer", command=self.clicked, fg_color="#001a35",
                           border_color="white", border_width=1)
        button.pack(pady=25)

    def create_alert(self) -> list[CTkLabel]:
        """
        FR : Méthode permettant de créer les alertes\n
        EN : Method to create alerts
        :return:
            FR :
            EN :
        """
        return [CTkLabel(master=self.frame, text="Veuillez entrer une clé API", fg_color="red", corner_radius=5),
                CTkLabel(master=self.frame, text="Veuillez assigner une touche principale", fg_color="red",
                         corner_radius=5),
                CTkLabel(master=self.frame, text="Veuillez assigner une touche secondaire", fg_color="red",
                         corner_radius=5)]

    def is_valid_form(self) -> bool:
        """
        FR : Méthode permettant de valider le formulaire\n
        EN : Method to validate the form
        :return:
            FR :
            EN :
        """
        valid = True
        if self.textbox.get() == "":
            self.alert[0].pack(pady=2)
            valid = False
        if self.main_button.get() == "":
            self.alert[1].pack(pady=2)
            valid = False
        if self.second_button.get() == "":
            self.alert[2].pack(pady=2)
            valid = False
        return valid

    def detect_key(self, capture_textbox):
        # TODO : Finir documentation
        """
        FR : Méthode permettant de détecter la touche appuyée\n
        EN : Method to detect the pressed key
        :param capture_textbox:
        :return:
        """
        self.dropdown.configure(state="disabled")
        start_time = time.time()
        joystick = pygame.joystick.Joystick(self.get_idx_device_selected())
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
        self.dropdown.configure(state="normal")

    def get_idx_device_selected(self) -> int:
        """
        FR : Méthode permettant de récupérer l'index du périphérique sélectionné\n
        EN : Method to get the index of the selected device
        :return:
            FR :
            EN :
        """
        self.dropdown.configure(state="disabled")
        return self.devices.index(self.dropdown.get())
