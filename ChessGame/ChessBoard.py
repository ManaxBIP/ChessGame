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
        self.calculated_moves = []

        self.piece_images = {}
        self.load_pieces()

        self.canvas = tk.Canvas(self)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.sidebar = tk.Frame(self)
        self.sidebar.pack(side="right", fill="y")

        self.white_captures_frame = tk.Frame(self.sidebar)
        self.white_captures_frame.pack()
        self.black_captures_frame = tk.Frame(self.sidebar)
        self.black_captures_frame.pack()

        self.white_points = 0
        self.black_points = 0

        self.white_captures_label = tk.Label(self.white_captures_frame, text="White Captures:")
        self.white_captures_label.pack()
        self.black_captures_label = tk.Label(self.black_captures_frame, text="Black Captures:")
        self.black_captures_label.pack()

        self.white_points_label = tk.Label(self.sidebar, text="")
        self.white_points_label.pack()
        self.black_points_label = tk.Label(self.sidebar, text="")
        self.black_points_label.pack()

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
        self.canvas.delete("move_indicator")
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

        self.draw_move_indicators(offset_x, offset_y)
        self.update_selection_rectangle(offset_x, offset_y)

    def draw_move_indicators(self, offset_x, offset_y):
        self.canvas.delete("move_indicator")
        for move in self.calculated_moves:
            col, row = move
            x = offset_x + col * self.size + self.size / 2
            y = offset_y + row * self.size + self.size / 2
            radius = self.size // 8
            color = "blue" if move not in self.pieces else "red"
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, tags="move_indicator")

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
            if not self.selected_piece:
                self.selected_piece = self.pieces[position]
                self.selected_position = position
                self.drag_data["item"] = self.canvas.find_withtag("current")
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y

                print(f"Selected piece: {self.selected_piece} at {position}")
                self.calculated_moves = self.validMoves(
                    self.Calculate_moves(self.selected_piece, self.selected_position))
            else:
                self.click_movement(position)
                # clear selection
                self.selected_piece = None
                self.calculated_moves = []
                # clear red outline
                self.update_selection_rectangle()
                self.refresh_board()
        else:
            self.click_movement(position)
            # clear selection
            self.selected_piece = None
            self.calculated_moves = []
            # clear red outline
            self.update_selection_rectangle()
            self.refresh_board()

    def click_movement(self, new_position):
        if self.selected_piece:
            if (new_position[0] < 0 or new_position[0] >= self.columns or
                    new_position[1] < 0 or new_position[1] >= self.rows):
                new_position = self.selected_position
            self.move_piece(self.selected_position, new_position)
            print(f"Selected position: {self.selected_position}, {new_position}")
            self.selected_position = None
            self.calculated_moves = []
            self.update_selection_rectangle()
            self.refresh_board()

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
                if new_position == self.selected_position:
                    self.selected_piece = new_position
                else:
                    self.selected_position = None
                    self.selected_piece = None
                    self.calculated_moves = []

                self.update_selection_rectangle()
                self.refresh_board()

            self.drag_data = {"x": 0, "y": 0, "item": None}

    def move_piece(self, from_pos, to_pos):
        if from_pos in self.pieces:
            if (to_pos in self.calculated_moves):
                captured_piece = self.pieces.pop(to_pos, None)  # Capture piece if present
                piece_to_move = self.pieces.pop(from_pos)  # Remove piece from original position
                self.pieces[to_pos] = piece_to_move  # Place the piece at the new position
                self.calculated_moves = []

                if captured_piece:
                    self.capture_piece(captured_piece)

            # Refresh the board to update the canvas
            self.refresh_board()

    def capture_piece(self, captured_piece):
        piece_name = captured_piece.split("_")[1]
        points = {"pawn": 1, "knight": 3, "bishop": 3, "rook": 5, "queen": 9, "king": 99}
        point_value = points.get(piece_name, 0)

        # Resize the image for captured piece
        capture_image = Image.open(f'Pieces/{captured_piece}.png').convert("RGBA")
        capture_image = capture_image.resize((self.size // 3, self.size // 3), Image.LANCZOS)
        capture_image = ImageTk.PhotoImage(capture_image)

        if captured_piece.startswith("white"):
            self.black_points += point_value
            capture_label = tk.Label(self.black_captures_frame, image=capture_image)
            capture_label.image = capture_image
            capture_label.pack()
        else:
            self.white_points += point_value
            capture_label = tk.Label(self.white_captures_frame, image=capture_image)
            capture_label.image = capture_image
            capture_label.pack()

        # Update points display only for the leading side
        if self.white_points > self.black_points:
            self.white_points_label.config(text=f"+{self.white_points - self.black_points}")
            self.black_points_label.config(text="")
        elif self.black_points > self.white_points:
            self.black_points_label.config(text=f"+{self.black_points - self.white_points}")
            self.white_points_label.config(text="")
        else:
            self.white_points_label.config(text="")
            self.black_points_label.config(text="")

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
                                                                    outline="yellow", width=3)

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
                direction = -1 if piece.split("_")[0] == "white" else 1
                start_row = 6 if piece.split("_")[0] == "white" else 1
                if position[1] == start_row:
                    if (position[0], position[1] + direction) not in self.pieces:
                        positions_available.append((position[0], position[1] + direction))
                    if (position[0], position[1] + 2 * direction) not in self.pieces:
                        positions_available.append((position[0], position[1] + 2 * direction))
                else:
                    if (position[0], position[1] + direction) not in self.pieces:
                        positions_available.append((position[0], position[1] + direction))

                # Capture moves
                capture_moves = [(position[0] + 1, position[1] + direction), (position[0] - 1, position[1] + direction)]
                for move in capture_moves:
                    if 0 <= move[0] < 8 and 0 <= move[1] < 8:
                        if move in self.pieces and self.pieces[move].split("_")[0] != piece.split("_")[0]:
                            positions_available.append(move)

                for pos in positions_available:
                    if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7:
                        continue
                    else:
                        positions_available_valide.append(pos)
                pass
            case _:
                print("Invalid piece name")
        return positions_available_valide

    def validMoves(self, calculateMoves: list) -> list:
        valid_moves = []
        piece_color = self.selected_piece.split("_")[0]
        piece_name = self.selected_piece.split("_")[1]

        def is_clear_path(start, end, step):
            current = start
            while current != end:
                if current in self.pieces:
                    return False
                current = (current[0] + step[0], current[1] + step[1])
            return True

        for move in calculateMoves:
            if piece_name in ["rook", "queen"]:
                if move[0] == self.selected_position[0]:  # Vertical move
                    step = (0, 1) if move[1] > self.selected_position[1] else (0, -1)
                    if is_clear_path((self.selected_position[0], self.selected_position[1] + step[1]), move, step):
                        if move in self.pieces:
                            if self.pieces[move].split("_")[0] != piece_color:
                                valid_moves.append(move)
                        else:
                            valid_moves.append(move)
                elif move[1] == self.selected_position[1]:  # Horizontal move
                    step = (1, 0) if move[0] > self.selected_position[0] else (-1, 0)
                    if is_clear_path((self.selected_position[0] + step[0], self.selected_position[1]), move, step):
                        if move in self.pieces:
                            if self.pieces[move].split("_")[0] != piece_color:
                                valid_moves.append(move)
                        else:
                            valid_moves.append(move)
            if piece_name in ["bishop", "queen"]:
                step_x = 1 if move[0] > self.selected_position[0] else -1
                step_y = 1 if move[1] > self.selected_position[1] else -1
                if abs(move[0] - self.selected_position[0]) == abs(
                        move[1] - self.selected_position[1]):  # Diagonal move
                    if is_clear_path((self.selected_position[0] + step_x, self.selected_position[1] + step_y), move,
                                     (step_x, step_y)):
                        if move in self.pieces:
                            if self.pieces[move].split("_")[0] != piece_color:
                                valid_moves.append(move)
                        else:
                            valid_moves.append(move)
            elif piece_name == "pawn":
                direction = -1 if piece_color == "white" else 1
                if move in self.pieces:
                    if move in [(self.selected_position[0] + 1, self.selected_position[1] + direction),
                                (self.selected_position[0] - 1, self.selected_position[1] + direction)]:
                        valid_moves.append(move)
                elif move not in self.pieces:
                    if move[0] == self.selected_position[0]:  # Ensure pawns don't move forward if blocked
                        valid_moves.append(move)
            else:
                if move in self.pieces:
                    if self.pieces[move].split("_")[0] != piece_color:
                        valid_moves.append(move)
                else:
                    valid_moves.append(move)

        return valid_moves
