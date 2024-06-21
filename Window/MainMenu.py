import tkinter as tk

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = tk.Label(self, text="ChessGame", font=("Helvetica", 24))
        self.label.pack(pady=20)

        self.play_button = tk.Button(self, text="Play Against IA", font=("Helvetica", 14), command=self.start_game)
        self.play_button.pack(pady=20)

        self.multiplayer_button = tk.Button(self, text="Multiplayer", font=("Helvetica", 14), command=self.start_multiplayer)
        self.multiplayer_button.pack(pady=20)

        self.quit_button = tk.Button(self, text="Quit", font=("Helvetica", 14), command=self.quit)
        self.quit_button.pack(pady=20)

    def start_game(self):
        self.controller.show_frame("ChessBoard")
    
    def start_multiplayer(self):
        self.controller.show_frame("MultiplayerMenu")