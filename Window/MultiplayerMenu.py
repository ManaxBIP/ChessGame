import tkinter as tk

class MultiplayerMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = tk.Label(self, text="Multiplayer", font=("Helvetica", 24))
        self.label.pack(pady=20)

        self.create_button = tk.Button(self, text="Create Match", font=("Helvetica", 14), command=self.create_match)
        self.create_button.pack(pady=20)

        self.join_button = tk.Button(self, text="Join Match", font=("Helvetica", 14), command=self.join_match)
        self.join_button.pack(pady=20)

        self.back_button = tk.Button(self, text="Back", font=("Helvetica", 14), command=self.go_back)
        self.back_button.pack(pady=20)

    def create_match(self):
        # Logique pour démarrer un serveur
        print("Create Match")
    
    def join_match(self):
        # Logique pour rejoindre un serveur
        print("Join Match")

    def go_back(self):
        self.controller.show_frame("MainMenu")