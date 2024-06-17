import tkinter as tk
from PIL import Image, ImageTk

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
        
        self.piece_images = {}
        self.load_pieces()

        self.canvas = tk.Canvas(self)
        self.canvas.pack(side="top", fill="both", expand=True)

        self.canvas.bind("<Configure>", self.refresh_board)

    def load_pieces(self):
        piece_names = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']
        colors = ['white', 'black']
        for color in colors:
            for piece in piece_names:
                png_file = f'Pieces/{color}_{piece}.png'
                image = Image.open(png_file)
                image = image.resize((self.size, self.size), Image.LANCZOS)
                self.piece_images[f'{color}_{piece}'] = ImageTk.PhotoImage(image)

    def draw_board(self, offset_x, offset_y):
        self.canvas.delete("square")
        self.canvas.delete("piece")
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
        
        # Draw the row numbers
        for row in range(self.rows):
            y = offset_y + row * self.size + self.size / 2
            self.canvas.create_text(offset_x - self.size / 2, y, text=str(self.rows - row), tags="square")

        # Draw the column letters
        letters = "abcdefgh"
        for col in range(self.columns):
            x = offset_x + col * self.size + self.size / 2
            self.canvas.create_text(x, offset_y + self.rows * self.size + self.size / 2, text=letters[col], tags="square")

        # Draw pieces
        for position, piece in self.pieces.items():
            col, row = position
            x = offset_x + col * self.size
            y = offset_y + row * self.size
            self.canvas.create_image(x + self.size / 2, y + self.size / 2, image=self.piece_images[piece], tags="piece")

    def refresh_board(self, event=None):
        '''Redraw the board, possibly in response to window being resized'''
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.size = min(int(canvas_width / (self.columns + 2)), int(canvas_height / (self.rows + 2)))

        # Calculate offset to center the board
        offset_x = (canvas_width - self.columns * self.size) / 2
        offset_y = (canvas_height - self.rows * self.size) / 2
        
        self.draw_board(offset_x, offset_y)


    def add_piece(self, piece, position):
        '''Add a piece to the board at the given position'''
        self.pieces[position] = piece
        # self.refresh_board()