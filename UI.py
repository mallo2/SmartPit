import time

import pygame
from PIL import Image
from customtkinter import CTkFrame, CTkImage, CTkLabel, CTkEntry, CTkComboBox, CTkButton
from dotenv import set_key, get_key


def update_env_file(api_key, selected_device, main_button, second_button):
    set_key('.env', 'GROQ_API_KEY', api_key)
    set_key('.env', 'SELECTED_DEVICE', selected_device)
    set_key('.env', 'MAIN_BUTTON', main_button)
    set_key('.env', 'SECOND_BUTTON', second_button)


def init_textbox(textbox):
    groq_api_key = get_key('.env', 'GROQ_API_KEY')
    if groq_api_key and groq_api_key != "":
        textbox.insert(0, groq_api_key)


def change_order_devices(devices):
    selected_device = get_key('.env', 'SELECTED_DEVICE')
    if selected_device and selected_device != "" and selected_device in devices:
        devices.remove(selected_device)
        devices.insert(0, selected_device)


def init_main(main):
    main.title("SmartPit")
    main.geometry("800x600")
    main.resizable(False, False)
    main.iconbitmap('ressources/images/favicon.ico')
    return main


class UI:
    def __init__(self, main, devices):
        self.devices = devices
        self.main = init_main(main)
        self.frame = self.create_frame()
        self.create_image()
        self.textbox = self.create_textbox()
        self.dropdown = self.create_dropdown(devices)
        self.main_button = self.create_button_textbox_frame("Assigner la touche principale ")
        self.second_button = self.create_button_textbox_frame("Assigner la touche secondaire")
        self.create_button()
        self.alert = self.create_alert()

    def clicked(self):
        from SmartPit import launch_application
        if self.is_valid_form():
            update_env_file(self.textbox.get(), self.dropdown.get(), self.main_button.get(), self.second_button.get())
            idx = self.devices.index(self.dropdown.get())
            self.main.destroy()
            launch_application(idx)

    def create_frame(self):
        frame = CTkFrame(master=self.main, fg_color="#001a35")
        frame.pack(pady=10, padx=30, fill="both", expand=True)
        return frame

    def create_image(self):
        logo = CTkImage(light_image=Image.open('ressources/images/logo.jpg'),
                        dark_image=Image.open('ressources/images/logo.jpg'), size=(150, 150))
        title = CTkLabel(master=self.frame, text="", image=logo)
        title.pack(pady=12, padx=10)

    def create_textbox(self):
        textbox = CTkEntry(self.frame, placeholder_text="GROQ API Key", height=25, width=250, border_width=1,
                           border_color="white")
        textbox.pack(pady=20)
        init_textbox(textbox)
        return textbox

    def create_dropdown(self, devices):
        devices_copy = devices.copy()
        change_order_devices(devices_copy)
        dropdown = CTkComboBox(self.frame, values=devices_copy, state="readonly", width=300)
        dropdown.set(devices_copy[0])
        dropdown.pack(pady=20)
        return dropdown

    def create_button_textbox_frame(self, text):
        frame = CTkFrame(master=self.frame, fg_color="#001a35")
        frame.pack(pady=5)
        capture_textbox = CTkEntry(frame, height=30, width=50)
        capture_textbox.pack(side="left")

        if text == "Assigner la touche principale ":
            capture_textbox.insert(0, get_key('.env', 'MAIN_BUTTON'))
            main_button = CTkButton(frame, text=text, command=self.detect_key_main)
        else:
            capture_textbox.insert(0, get_key('.env', 'SECOND_BUTTON'))
            main_button = CTkButton(frame, text=text, command=self.detect_key_second)

        capture_textbox.configure(state="readonly")
        main_button.pack(side="left", padx=5)

        return capture_textbox

    def create_button(self):
        button = CTkButton(master=self.frame, text="Démarrer", command=self.clicked, fg_color="#001a35",
                           border_color="white", border_width=1)
        button.pack(pady=25)

    def create_alert(self):
        return [CTkLabel(master=self.frame, text="Veuillez entrer une clé API", fg_color="red", corner_radius=5),
                CTkLabel(master=self.frame, text="Veuillez assigner une touche principale", fg_color="red",
                         corner_radius=5),
                CTkLabel(master=self.frame, text="Veuillez assigner une touche secondaire", fg_color="red",
                         corner_radius=5)]

    def is_valid_form(self):
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

    def detect_key_main(self):
        self.dropdown.configure(state="disabled")
        start_time = time.time()
        joystick = pygame.joystick.Joystick(2)
        joystick.init()
        while True:
            if time.time() - start_time > 7.5:
                break
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    self.main_button.delete(0, "end")
                    self.main_button.configure(state="normal")
                    self.main_button.insert(0, f"{event.button}")
                    self.main_button.configure(state="readonly")
                    return
            pygame.time.wait(100)
        self.dropdown.configure(state="normal")

    def detect_key_second(self):
        self.dropdown.configure(state="disabled")
        start_time = time.time()
        # TODO: change the index of the joystick
        joystick = pygame.joystick.Joystick(2)
        joystick.init()
        while True:
            if time.time() - start_time > 7.5:
                break
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    self.second_button.delete(0, "end")
                    self.second_button.configure(state="normal")
                    self.second_button.insert(0, f"{event.button}")
                    self.second_button.configure(state="readonly")
                    return
            pygame.time.wait(100)
        self.dropdown.configure(state="normal")
