import tkinter as tk

class ChessBoard(tk.Frame):
    def __init__(self, parent, rows=8, columns=8, size=64, color1="white", color2="purple"):
        '''size is the size of a square, in pixels'''
        super().__init__(parent)
        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.color2 = color2
        self.pieces = {}

        self.canvas = tk.Canvas(self)
        self.canvas.pack(side="top", fill="both", expand=True)

        self.canvas.bind("<Configure>", self.refresh_board)

    def draw_board(self, offset_x, offset_y):
        self.canvas.delete("square")
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                x1 = offset_x + col * self.size
                y1 = offset_y + row * self.size
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                color = self.color1 if color == self.color2 else self.color2

    def refresh_board(self, event=None):
        '''Redraw the board, possibly in response to window being resized'''
        canvas_width = event.width
        canvas_height = event.height
        self.size = min(int(canvas_width / self.columns), int(canvas_height / self.rows))

        # Calculate offset to center the board
        offset_x = (canvas_width - self.columns * self.size) / 2
        offset_y = (canvas_height - self.rows * self.size) / 2

        self.draw_board(offset_x, offset_y)

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = tk.Label(self, text="ChessGame", font=("Helvetica", 24))
        self.label.pack(pady=20)

        self.play_button = tk.Button(self, text="Play", font=("Helvetica", 14), command=self.start_game)
        self.play_button.pack(pady=20)

    def start_game(self):
        self.controller.show_frame("ChessBoard")

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
