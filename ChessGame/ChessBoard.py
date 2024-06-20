import tkinter as tk
from PIL import Image, ImageTk


class ChessBoard(tk.Frame):
    def __init__(self, parent, rows=8, columns=8, size=64, color1="white", color2="purple"):
        super().__init__(parent)
        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.color2 = color2
        self.pieces = {}
        self.selected_piece = None
        self.selected_position = None
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.selection_rectangle = None

        self.piece_images = {}
        self.load_pieces()

        self.canvas = tk.Canvas(self)
        self.canvas.pack(side="top", fill="both", expand=True)

        self.canvas.bind("<Configure>", self.refresh_board)
        self.canvas.bind("<ButtonPress-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)

    def load_pieces(self):
        piece_names = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']
        colors = ['white', 'black']
        for color in colors:
            for piece in piece_names:
                png_file = f'Pieces/{color}_{piece}.png'
                image = Image.open(png_file).convert("RGBA")
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

        for row in range(self.rows):
            y = offset_y + row * self.size + self.size / 2
            self.canvas.create_text(offset_x - self.size / 2, y, text=str(self.rows - row), tags="square")

        letters = "abcdefgh"
        for col in range(self.columns):
            x = offset_x + col * self.size + self.size / 2
            self.canvas.create_text(x, offset_y + self.rows * self.size + self.size / 2, text=letters[col],
                                    tags="square")

        for position, piece in self.pieces.items():
            col, row = position
            x = offset_x + col * self.size
            y = offset_y + row * self.size
            self.canvas.create_image(x + self.size / 2, y + self.size / 2, image=self.piece_images[piece],
                                     tags=("piece", position))

        self.update_selection_rectangle(offset_x, offset_y)

    def refresh_board(self, event=None):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.size = min(int(canvas_width / (self.columns + 2)), int(canvas_height / (self.rows + 2)))

        offset_x = (canvas_width - self.columns * self.size) / 2
        offset_y = (canvas_height - self.rows * self.size) / 2

        self.draw_board(offset_x, offset_y)

    def piece_location(self, event) -> tuple:
        col = (event.x - (self.canvas.winfo_width() - self.columns * self.size) / 2) // self.size
        row = (event.y - (self.canvas.winfo_height() - self.rows * self.size) / 2) // self.size
        return int(col), int(row)

    def on_click(self, event):
        position = self.piece_location(event)

        if position in self.pieces:
            self.selected_piece = self.pieces[position]
            self.selected_position = position
            self.drag_data["item"] = self.canvas.find_withtag("current")
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

            print(f"Selected piece: {self.selected_piece} at {position}")
        else:
            self.click_movement(position)

        self.update_selection_rectangle()

    def click_movement(self, new_position):
        if self.selected_piece:
            if (new_position[0] < 0 or new_position[0] >= self.columns or
                    new_position[1] < 0 or new_position[1] >= self.rows):
                new_position = self.selected_position
            self.move_piece(self.selected_position, new_position)
            self.selected_position = new_position
            self.update_selection_rectangle()

    def on_drag(self, event):
        if self.drag_data["item"]:
            delta_x = event.x - self.drag_data["x"]
            delta_y = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["item"], delta_x, delta_y)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_drop(self, event):
        if self.drag_data["item"]:
            new_position = self.piece_location(event)
            if self.selected_piece:
                if (new_position[0] < 0 or new_position[0] >= self.columns or
                        new_position[1] < 0 or new_position[1] >= self.rows):
                    new_position = self.selected_position
                self.move_piece(self.selected_position, new_position)
                self.selected_position = new_position
                self.update_selection_rectangle()

            self.drag_data = {"x": 0, "y": 0, "item": None}

    def move_piece(self, from_pos, to_pos):
        if from_pos in self.pieces:
            self.pieces[to_pos] = self.pieces.pop(from_pos)
            self.refresh_board()

    def add_piece(self, piece, position):
        self.pieces[position] = piece
        self.refresh_board()

    def update_selection_rectangle(self, offset_x=None, offset_y=None):
        if self.selection_rectangle:
            self.canvas.delete(self.selection_rectangle)
        if self.selected_position:
            if offset_x is None:
                offset_x = (self.canvas.winfo_width() - self.columns * self.size) / 2
            if offset_y is None:
                offset_y = (self.canvas.winfo_height() - self.rows * self.size) / 2
            col, row = self.selected_position
            x1 = offset_x + col * self.size
            y1 = offset_y + row * self.size
            self.selection_rectangle = self.canvas.create_rectangle(x1, y1, x1 + self.size, y1 + self.size,
                                                                    outline="red", width=3)
