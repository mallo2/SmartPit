from PIL import Image

import customtkinter as ctk

class UI:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.root = ctk.CTk()
        self.root.title("SmartPit")
        self.root.geometry("800x600")

        self.frame = ctk.CTkFrame(master=self.root, fg_color="#001a35")
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

        self.logo = ctk.CTkImage(light_image=Image.open('images/logo.jpg'),
                                 dark_image=Image.open('images/logo.jpg'), size=(150, 150))
        self.title = ctk.CTkLabel(master=self.frame, text="", image=self.logo)
        self.title.pack(pady=12, padx=10)

        self.textbox = ctk.CTkEntry(self.frame, placeholder_text="GROQ API Key", height=25, width=250, border_width=1,
                                    border_color="white")
        self.textbox.pack(pady=20)

        # Création de la liste déroulante
        options = ["Option 1", "Option 2", "Option 3", "Option 4"]
        self.dropdown = ctk.CTkComboBox(self.frame, values=options)
        self.dropdown.pack(pady=20)

        # Création du bouton
        self.button = ctk.CTkButton(master=self.frame, text="Démarrer", command=self.clicked)
        self.button.pack(pady=20)

        self.root.mainloop()

    def clicked(self):
        # Action à réaliser lors du clic sur le bouton
        print(f"API Key: {self.textbox.get()}")
        print(f"Option sélectionnée: {self.dropdown.get()}")

