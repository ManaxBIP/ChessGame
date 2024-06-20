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
                image = Image.open(png_file).convert("RGBA")  # Ensure the image has an alpha channel
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
            self.canvas.create_image(x + self.size / 2, y + self.size / 2, image=self.piece_images[piece], tags=("piece", position))

    def refresh_board(self, event=None):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.size = min(int(canvas_width / (self.columns + 2)), int(canvas_height / (self.rows + 2)))

        # Calculate offset to center the board
        offset_x = (canvas_width - self.columns * self.size) / 2
        offset_y = (canvas_height - self.rows * self.size) / 2

        self.draw_board(offset_x, offset_y)

    def on_click(self, event):
        # record the item and its location
        col = (event.x - (self.canvas.winfo_width() - self.columns * self.size) / 2) // self.size
        row = (event.y - (self.canvas.winfo_height() - self.rows * self.size) / 2) // self.size
        position = (int(col), int(row))

        if position in self.pieces:
            self.selected_piece = self.pieces[position]
            self.selected_position = position
            print(self.Calculate_moves(self.selected_piece, self.selected_position))
            self.drag_data["item"] = self.canvas.find_withtag("current")
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_drag(self, event):
        if self.drag_data["item"]:
            # compute how much the mouse has moved
            delta_x = event.x - self.drag_data["x"]
            delta_y = event.y - self.drag_data["y"]
            # move the object the appropriate amount
            self.canvas.move(self.drag_data["item"], delta_x, delta_y)
            # record the new position
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_drop(self, event):
        if self.drag_data["item"]:
            col = (event.x - (self.canvas.winfo_width() - self.columns * self.size) / 2) // self.size
            row = (event.y - (self.canvas.winfo_height() - self.rows * self.size) / 2) // self.size
            new_position = (int(col), int(row))
            if self.selected_piece:
                if (new_position[0] < 0 or new_position[0] >= self.columns or
                        new_position[1] < 0 or new_position[1] >= self.rows):
                    new_position = self.selected_position
                self.move_piece(self.selected_position, new_position)
                self.selected_piece = None
                self.selected_position = None

            # reset the drag data
            self.drag_data = {"x": 0, "y": 0, "item": None}

    def move_piece(self, from_pos, to_pos):
        if from_pos in self.pieces:
            self.pieces[to_pos] = self.pieces.pop(from_pos)
            self.refresh_board()

    def add_piece(self, piece, position):
        self.pieces[position] = piece
        self.refresh_board()

    def Calculate_moves(self, piece, position):
        piece_name = piece.split("_")[1]
        positions_available = []
        positions_available_valide = []
        match piece_name:
            case "king":
                # Calculate moves for king
                positions_available.append((position[0] + 1, position[1]))
                positions_available.append((position[0] - 1, position[1]))
                positions_available.append((position[0], position[1] + 1))
                positions_available.append((position[0], position[1] - 1))
                positions_available.append((position[0] + 1, position[1] + 1))
                positions_available.append((position[0] - 1, position[1] + 1))
                positions_available.append((position[0] + 1, position[1] - 1))
                positions_available.append((position[0] - 1, position[1] - 1))
                for pos in positions_available:
                    if pos[0] < 0 or pos[0] >= 8 or pos[1] < 0 or pos[1] >= 8:
                       continue
                    else:
                        positions_available_valide.append(pos)
                pass
            case "queen":
                # Calculate moves for queen
                for i in range(1, 8):
                    positions_available.append((position[0] + i, position[1]))
                    positions_available.append((position[0] - i, position[1]))
                    positions_available.append((position[0], position[1] + i))
                    positions_available.append((position[0], position[1] - i))
                    positions_available.append((position[0] + i, position[1] + i))
                    positions_available.append((position[0] - i, position[1] + i))
                    positions_available.append((position[0] + i, position[1] - i))
                    positions_available.append((position[0] - i, position[1] - i))
                for pos in positions_available:
                    if pos[0] < 0 or pos[0] >= 8 or pos[1] < 0 or pos[1] >= 8:
                       continue
                    else:
                        positions_available_valide.append(pos)
                pass
            case "rook":
                # Calculate moves for rook
                for i in range(1, 8):
                    positions_available.append((position[0] + i, position[1]))
                    positions_available.append((position[0] - i, position[1]))
                    positions_available.append((position[0], position[1] + i))
                    positions_available.append((position[0], position[1] - i))
                for pos in positions_available:
                    if pos[0] < 0 or pos[0] >= 8 or pos[1] < 0 or pos[1] >= 8:
                       continue
                    else:
                        positions_available_valide.append(pos)
                pass
            case "bishop":
                # Calculate moves for bishop
                for i in range(1, 8):
                    positions_available.append((position[0] + i, position[1] + i))
                    positions_available.append((position[0] - i, position[1] + i))
                    positions_available.append((position[0] + i, position[1] - i))
                    positions_available.append((position[0] - i, position[1] - i))
                for pos in positions_available:
                    if pos[0] < 0 or pos[0] >= 8 or pos[1] < 0 or pos[1] >= 8:
                       continue
                    else:
                        positions_available_valide.append(pos)
                positions_available = positions_available_valide
                pass
            case "knight":
                # Calculate moves for knight
                positions_available.append((position[0] + 1, position[1] + 2))
                positions_available.append((position[0] - 1, position[1] + 2))
                positions_available.append((position[0] + 1, position[1] - 2))
                positions_available.append((position[0] - 1, position[1] - 2))
                positions_available.append((position[0] + 2, position[1] + 1))
                positions_available.append((position[0] - 2, position[1] + 1))
                positions_available.append((position[0] + 2, position[1] - 1))
                positions_available.append((position[0] - 2, position[1] - 1))
                for pos in positions_available:
                    if pos[0] < 0 or pos[0] >= 8 or pos[1] < 0 or pos[1] >= 8:
                       continue
                    else:
                        positions_available_valide.append(pos)
                pass
            case "pawn":
                # Calculate moves for pawn
                if (position[1] == 6 and piece.split("_")[0] == "white") or (position[1] == 1 and piece.split("_")[0] == "black"):
                    if (piece.split("_")[0] == "white"):
                        positions_available.append((position[0], position[1] - 1))
                        positions_available.append((position[0], position[1] - 2))
                    else:
                        positions_available.append((position[0], position[1] + 1))
                        positions_available.append((position[0], position[1] + 2))
                else:
                    if (piece.split("_")[0] == "white"):
                        positions_available.append((position[0], position[1] - 1))
                    else:
                        positions_available.append((position[0], position[1] + 1))
                for pos in positions_available:
                    if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7:
                       continue
                    else:
                        positions_available_valide.append(pos)
                pass
            case _:
                print("Invalid piece name")
        return positions_available_valide