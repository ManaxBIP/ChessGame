
import tkinter as tk
from ChessGame.ChessBoard import *
from Window.MainMenu import MainMenu

class ChessApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChessGame")
        self.geometry("800x800")
        self.minsize(800, 800)

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainMenu, ChessBoard):
            page_name = F.__name__
            if F == ChessBoard:
                frame = F(parent=self.container)  # ChessBoard n'a pas besoin de controller
                frame.add_piece('white_king', (4, 7))
                frame.add_piece('black_king', (4, 0))
                frame.add_piece('white_queen', (3, 7))
                frame.add_piece('black_queen', (3, 0))
                frame.add_piece('white_rook', (0, 7))
                frame.add_piece('white_rook', (7, 7))
                frame.add_piece('black_rook', (0, 0))
                frame.add_piece('black_rook', (7, 0))
                frame.add_piece('white_bishop', (2, 7))
                frame.add_piece('white_bishop', (5, 7))
                frame.add_piece('black_bishop', (2, 0))
                frame.add_piece('black_bishop', (5, 0))
                frame.add_piece('white_knight', (1, 7))
                frame.add_piece('white_knight', (6, 7))
                frame.add_piece('black_knight', (1, 0))
                frame.add_piece('black_knight', (6, 0))
                for i in range(8):
                    frame.add_piece('white_pawn', (i, 6))
                    frame.add_piece('black_pawn', (i, 1))
                
            else:
                frame = F(parent=self.container, controller=self)  # MainMenu a besoin de controller
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
