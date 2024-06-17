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
