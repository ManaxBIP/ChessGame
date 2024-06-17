
import tkinter as tk
from ChessGame.ChessBoard import *
from Window.MainMenu import MainMenu

class ChessApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChessGame")
        self.geometry("600x600")

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainMenu, ChessBoard):
            page_name = F.__name__
            if F == ChessBoard:
                frame = F(parent=self.container)  # ChessBoard n'a pas besoin de controller
            else:
                frame = F(parent=self.container, controller=self)  # MainMenu a besoin de controller
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
