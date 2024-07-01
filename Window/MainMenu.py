import tkinter as tk

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = tk.Label(self, text="ChessGame", font=("Helvetica", 24))
        self.label.pack(pady=20)

        self.play_button = tk.Button(self, text="Play", font=("Helvetica", 14), command=self.start_game)
        self.play_button.pack(pady=20)

    def start_game(self):
        chess_board_frame = self.controller.frames["ChessBoard"]
        chess_board_frame.reset_board()
        self.controller.show_frame("ChessBoard")
