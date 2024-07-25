from PIL import Image
from customtkinter import CTkFrame, CTkImage, CTkLabel, CTkEntry, CTkComboBox, CTkButton
from dotenv import set_key, get_key


def update_env_file(api_key, selected_device):
    set_key('.env', 'GROQ_API_KEY', api_key)
    set_key('.env', 'SELECTED_DEVICE', selected_device)


def init_textbox(textbox):
    groq_api_key = get_key('.env', 'GROQ_API_KEY')
    if groq_api_key and groq_api_key != "":
        textbox.insert(0, groq_api_key)


def change_order_devices(devices):
    selected_device = get_key('.env', 'SELECTED_DEVICE')
    if selected_device and selected_device != "":
        devices.remove(selected_device)
        devices.insert(0, selected_device)


def init_main(main):
    main.title("SmartPit")
    main.geometry("800x600")
    return main


class UI:
    def __init__(self, main, devices):
        self.main = init_main(main)
        self.frame = self.create_frame()
        self.create_image()
        self.textbox = self.create_textbox()
        self.dropdown = self.create_dropdown(devices)
        self.create_button()
        self.alert = self.create_alert()

    def clicked(self):
        from SmartPit import launch_application
        self.show_alert_if_needed()
        update_env_file(self.textbox.get(), self.dropdown.get())
        self.main.destroy()
        launch_application()

    def create_frame(self):
        frame = CTkFrame(master=self.main, fg_color="#001a35")
        frame.pack(pady=20, padx=60, fill="both", expand=True)
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
        change_order_devices(devices)
        dropdown = CTkComboBox(self.frame, values=devices)
        dropdown.pack(pady=20)
        return dropdown

    def create_button(self):
        button = CTkButton(master=self.frame, text="Démarrer", command=self.clicked)
        button.pack(pady=20)

    def create_alert(self):
        alert = CTkLabel(master=self.frame, text="Veuillez entrer une clé API", fg_color="red", corner_radius=5)
        return alert

    def show_alert_if_needed(self):
        if self.textbox.get() == "":
            self.alert.pack(pady=10)
            return
