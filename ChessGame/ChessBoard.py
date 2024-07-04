import random
import tkinter as tk
from tkinter import messagebox
import os
import pandas as pd
import numpy as np
from PIL import Image, ImageTk
import ast

class ChessBoard(tk.Frame):
    def __init__(self, parent, controller, rows=8, columns=8, size=64, color1="white", color2="purple"):
        super().__init__(parent)
        self.controller = controller
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
        self.calculated_moves = np.array([])

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

        self.current_turn = "white"  # Initial turn set to white

        self.player_color = random.choice(["white", "black"])

        self.white_captures_label = tk.Label(self.white_captures_frame, text="White Captures:")
        self.white_captures_label.pack()
        self.black_captures_label = tk.Label(self.black_captures_frame, text="Black Captures:")
        self.black_captures_label.pack()

        self.turn_label = tk.Label(self.sidebar, text=f"Turn: {self.current_turn}")
        self.turn_label.pack()

        self.white_points_label = tk.Label(self.sidebar, text="")
        self.white_points_label.pack()
        self.black_points_label = tk.Label(self.sidebar, text="")
        self.black_points_label.pack()

        self.black_moves = []
        self.white_moves = []

        self.moves_of_game = {
            "white": self.white_moves,
            "black": self.black_moves
        }

        self.canvas.bind("<Configure>", self.refresh_board)
        self.canvas.bind("<ButtonPress-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)

        self.current_turn = "white"  # Initial turn set to white

        self.kings_moved = {'white': False, 'black': False}
        self.rooks_moved = {
            'white': {'left': False, 'right': False},
            'black': {'left': False, 'right': False}
        }

        self.add_pieces()

        self.csv_file = "chess_game_data.csv"
        if not os.path.exists(self.csv_file):
            self.initialize_csv()

    def initialize_csv(self):
        df = pd.DataFrame(columns=["Player Color", "IA Color", "Moves", "White Score", "Black Score", "Result"])
        df.to_csv(self.csv_file, index=False)

    def record_move(self, from_pos, to_pos):
        move = [from_pos, to_pos]
        if self.current_turn == "white":
            self.white_moves.append({"Move": move, "Value": self.evaluate_move(from_pos, to_pos)})
        else:
            self.black_moves.append({"Move": move, "Value": self.evaluate_move(from_pos, to_pos)})

    def record_game(self, moves, result):
        df = pd.read_csv(self.csv_file)
        new_row = {
            "Player Color": self.player_color,
            "IA Color": "black" if self.player_color == "white" else "white",
            "Moves": moves,
            "White Score": self.white_points,
            "Black Score": self.black_points,
            "Result": result
        }
        df = df._append(new_row, ignore_index=True)
        df.to_csv(self.csv_file, index=False)

    def load_pieces(self):
        piece_names = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']
        colors = ['white', 'black']
        for color in colors:
            for piece in piece_names:
                png_file = f'Pieces/{color}_{piece}.png'
                image = Image.open(png_file).convert("RGBA")
                image = image.resize((self.size, self.size), Image.LANCZOS)
                self.piece_images[f'{color}_{piece}'] = ImageTk.PhotoImage(image)

    def add_pieces(self):
        # Add pieces to the board
        pieces_layout = {
            'white': [
                ('rook', 0, 7), ('knight', 1, 7), ('bishop', 2, 7), ('queen', 3, 7), ('king', 4, 7), ('bishop', 5, 7), ('knight', 6, 7), ('rook', 7, 7),
                ('pawn', 0, 6), ('pawn', 1, 6), ('pawn', 2, 6), ('pawn', 3, 6), ('pawn', 4, 6), ('pawn', 5, 6), ('pawn', 6, 6), ('pawn', 7, 6)
            ],
            'black': [
                ('rook', 0, 0), ('knight', 1, 0), ('bishop', 2, 0), ('queen', 3, 0), ('king', 4, 0), ('bishop', 5, 0), ('knight', 6, 0), ('rook', 7, 0),
                ('pawn', 0, 1), ('pawn', 1, 1), ('pawn', 2, 1), ('pawn', 3, 1), ('pawn', 4, 1), ('pawn', 5, 1), ('pawn', 6, 1), ('pawn', 7, 1)
            ]
        }
        for color, pieces in pieces_layout.items():
            for piece, col, row in pieces:
                self.add_piece(f"{color}_{piece}", (col, row))

    def draw_board(self, offset_x, offset_y):
        self.canvas.delete("square")
        self.canvas.delete("piece")
        self.canvas.delete("move_indicator")
        color = self.color2

        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                if self.player_color == "white":
                    x1 = offset_x + col * self.size
                    y1 = offset_y + row * self.size
                else:
                    x1 = offset_x + (self.columns - 1 - col) * self.size
                    y1 = offset_y + (self.rows - 1 - row) * self.size

                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                color = self.color1 if color == self.color2 else self.color2

        for row in range(self.rows):
            if self.player_color == "white":
                y = offset_y + row * self.size + self.size / 2
                self.canvas.create_text(offset_x - self.size / 2, y, text=str(self.rows - row), tags="square")
            else:
                y = offset_y + (self.rows - 1 - row) * self.size + self.size / 2
                self.canvas.create_text(offset_x - self.size / 2, y, text=str(self.rows - row), tags="square")

        letters = "abcdefgh"
        if self.player_color == "black":
            letters = letters[::-1]
        for col in range(self.columns):
            if self.player_color == "white":
                x = offset_x + col * self.size + self.size / 2
                self.canvas.create_text(x, offset_y + self.rows * self.size + self.size / 2, text=letters[col], tags="square")
            else:
                x = offset_x + (self.columns - 1 - col) * self.size + self.size / 2
                self.canvas.create_text(x, offset_y + self.rows * self.size + self.size / 2, text=letters[self.columns - 1 - col], tags="square")

        for position, piece in self.pieces.items():
            col, row = position
            if self.player_color == "white":
                x = offset_x + col * self.size
                y = offset_y + row * self.size
            else:
                x = offset_x + (self.columns - 1 - col) * self.size
                y = offset_y + (self.rows - 1 - row) * self.size

            self.canvas.create_image(x + self.size / 2, y + self.size / 2, image=self.piece_images[piece],
                                     tags=("piece", position))

        if self.current_turn == self.player_color:
            self.draw_move_indicators(offset_x, offset_y)
            self.update_selection_rectangle(offset_x, offset_y)

    def draw_move_indicators(self, offset_x, offset_y):
        self.canvas.delete("move_indicator")
        for move in self.calculated_moves:
            col, row = move
            if self.player_color == "white":
                x = offset_x + col * self.size + self.size / 2
                y = offset_y + row * self.size + self.size / 2
            else:
                x = offset_x + (self.columns - 1 - col) * self.size + self.size / 2
                y = offset_y + (self.rows - 1 - row) * self.size + self.size / 2
            radius = self.size // 8
            color = "blue" if tuple(move) not in self.pieces else "red"
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, tags="move_indicator")

    def refresh_board(self, event=None):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.size = min(int(canvas_width / (self.columns + 2)), int(canvas_height / (self.rows + 2)))

        offset_x = (canvas_width - self.columns * self.size) / 2
        offset_y = (canvas_height - self.rows * self.size) / 2

        self.draw_board(offset_x, offset_y)
        if self.current_turn != self.player_color:
            self.after(1000, self.ai_move)

    def piece_location(self, event) -> tuple:
        col = (event.x - (self.canvas.winfo_width() - self.columns * self.size) / 2) // self.size
        row = (event.y - (self.canvas.winfo_height() - self.rows * self.size) / 2) // self.size

        col = int(col)
        row = int(row)

        if self.player_color == "black":
            col = self.columns - 1 - col
            row = self.rows - 1 - row

        return col, row

    def on_click(self, event):
        position = self.piece_location(event)

        if self.current_turn == self.player_color:
            if self.selected_piece and self.selected_position:
                if tuple(position) in map(tuple, self.calculated_moves):
                    self.click_movement(position)
                    self.selected_piece = None
                    self.selected_position = None
                    self.calculated_moves = np.array([])
                    self.update_selection_rectangle()
                    self.refresh_board()
                else:
                    self.selected_piece = None
                    self.selected_position = None
                    self.calculated_moves = np.array([])
                    self.update_selection_rectangle()
                    self.refresh_board()
            else:
                if tuple(position) in self.pieces:
                    if self.pieces[tuple(position)].split("_")[0] == self.current_turn:
                        self.selected_piece = self.pieces[tuple(position)]
                        self.selected_position = position
                        self.drag_data["item"] = self.canvas.find_withtag("current")
                        self.drag_data["x"] = event.x
                        self.drag_data["y"] = event.y
                        self.calculated_moves = np.array(self.validMoves(self.selected_piece, self.selected_position,
                                                                self.Calculate_moves(self.selected_piece,
                                                                                     self.selected_position)))
                        self.update_selection_rectangle()
                        self.draw_move_indicators((self.canvas.winfo_width() - self.columns * self.size) / 2,
                                                  (self.canvas.winfo_height() - self.rows * self.size) / 2)

    def click_movement(self, new_position):
        if self.selected_piece and self.current_turn == self.player_color:
            if (new_position[0] < 0 or new_position[0] >= self.columns or
                    new_position[1] < 0 or new_position[1] >= self.rows):
                new_position = self.selected_position
            if self.move_piece(self.selected_position, new_position, True):
                self.current_turn = "black" if self.current_turn == "white" else "white"
            self.selected_position = None
            self.calculated_moves = np.array([])
            self.update_selection_rectangle()
            self.refresh_board()

    def on_drag(self, event):
        if self.drag_data["item"] and self.current_turn == self.player_color:
            delta_x = event.x - self.drag_data["x"]
            delta_y = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["item"], delta_x, delta_y)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            offset_x = (self.canvas.winfo_width() - self.columns * self.size) / 2
            offset_y = (self.canvas.winfo_height() - self.rows * self.size) / 2
            self.draw_move_indicators(offset_x, offset_y)
            self.canvas.tag_raise(self.drag_data["item"])

    def on_drop(self, event):
        if self.drag_data["item"] and self.current_turn == self.player_color:
            new_position = self.piece_location(event)
            if self.selected_piece:
                if (new_position[0] < 0 or new_position[0] >= self.columns or
                        new_position[1] < 0 or new_position[1] >= self.rows):
                    new_position = self.selected_position
                if self.move_piece(self.selected_position, new_position, True):
                    self.current_turn = "black" if self.current_turn == "white" else "white"
                self.update_selection_rectangle()
                self.refresh_board()

            self.drag_data = {"x": 0, "y": 0, "item": None}

    def move_piece(self, from_pos, to_pos, record=True):
        if record:
            self.record_move(from_pos, to_pos)
        if from_pos in self.pieces:
            piece = self.pieces[from_pos]
            piece_color = piece.split("_")[0]
            piece_type = piece.split("_")[1]
            
            # Vérifier et effectuer le roque
            if piece_type == "king" and abs(from_pos[0] - to_pos[0]) == 2:
                if not self.perform_castling(from_pos, to_pos):
                    return False  # Cannot castle if it puts the king in check
                return True

            if to_pos in self.validMoves(piece, from_pos, self.Calculate_moves(piece, from_pos)):
                captured_piece = self.pieces.pop(to_pos, None)
                piece_to_move = self.pieces.pop(from_pos)
                self.pieces[to_pos] = piece_to_move
                self.calculated_moves = []
                if captured_piece:
                    self.capture_piece(captured_piece)

                # Mettre à jour les états de mouvement du roi et des tours
                if piece_type == "king":
                    self.kings_moved[piece_color] = True
                elif piece_type == "rook":
                    if from_pos == (0, 0) or from_pos == (0, 7):
                        self.rooks_moved[piece_color]['left'] = True
                    elif from_pos == (7, 0) or from_pos == (7, 7):
                        self.rooks_moved[piece_color]['right'] = True

                # Vérifier si le mouvement laisse le roi en échec
                if self.check_for_check(self.current_turn):
                    # Revenir en arrière si le roi est en échec
                    self.pieces[from_pos] = self.pieces.pop(to_pos)
                    if captured_piece:
                        self.pieces[to_pos] = captured_piece
                    return False
                else:
                    # Promotion du pion
                    if piece_type == "pawn" and (to_pos[1] == 0 or to_pos[1] == 7):
                        self.promote_pawn(to_pos)

                    opponent_color = "black" if self.current_turn == "white" else "white"
                    if self.check_for_checkmate(opponent_color):
                        self.show_checkmate_message(self.current_turn)
                    elif self.check_for_draw(opponent_color):
                        pass

                    self.selected_position = None
                    self.selected_piece = None
                    return True

            self.refresh_board()
            return False
        return False

    def perform_castling(self, king_pos, new_king_pos):
        row = king_pos[1]
        if new_king_pos[0] == 2:
            rook_pos = (0, row)
            new_rook_pos = (3, row)
        elif new_king_pos[0] == 6:
            rook_pos = (7, row)
            new_rook_pos = (5, row)

        if self.check_positions_for_attack(self.current_turn, [king_pos, new_king_pos, rook_pos]):
            return False  # Cannot castle through check

        self.pieces[new_king_pos] = self.pieces.pop(king_pos)
        self.pieces[new_rook_pos] = self.pieces.pop(rook_pos)
        self.kings_moved[self.pieces[new_king_pos].split("_")[0]] = True
        if new_rook_pos[0] == 3:
            self.rooks_moved[self.pieces[new_rook_pos].split("_")[0]]['left'] = True
        else:
            self.rooks_moved[self.pieces[new_rook_pos].split("_")[0]]['right'] = True

        self.refresh_board()
        return True

    def ai_move(self):
        if self.current_turn != self.player_color:
            similar_games = self.analyze_csv()
            evaluation_adjustments = self.adjust_move_evaluation(similar_games)
            
            possible_moves = []
            pieces_copy = list(self.pieces.items())

            for pos, piece in pieces_copy:
                if piece.split("_")[0] == self.current_turn:
                    valid_moves = self.validMoves(piece, pos, self.Calculate_moves(piece, pos))
                    for move in valid_moves:
                        move_score = self.evaluate_move(pos, move)
                        
                        if (pos, move) in evaluation_adjustments:
                            move_score += evaluation_adjustments[(pos, move)]
                            
                        possible_moves.append((move_score, pos, move))

            if possible_moves:
                # Trier les mouvements par score de manière décroissante
                possible_moves.sort(reverse=True, key=lambda x: x[0])

                # Filtrer les mouvements qui ne laissent pas le roi en échec
                safe_moves = []
                for move in possible_moves:
                    from_pos, to_pos = move[1], move[2]
                    original_piece = self.pieces.get(tuple(to_pos))
                    self.pieces[tuple(to_pos)] = self.pieces.pop(tuple(from_pos))
                    if not self.check_for_check(self.current_turn):
                        safe_moves.append(move)
                    self.pieces[tuple(from_pos)] = self.pieces.pop(tuple(to_pos))
                    if original_piece:
                        self.pieces[tuple(to_pos)] = original_piece

                if safe_moves:
                    # Si des mouvements sûrs existent, choisir le meilleur
                    best_move = safe_moves[0]
                else:
                    best_move = possible_moves[0]

                from_pos, to_pos = best_move[1], best_move[2]
                self.move_piece(from_pos, to_pos, record=False)  # Désactiver l'enregistrement pour les mouvements IA
                self.current_turn = "white" if self.current_turn == "black" else "black"
                self.refresh_board()
                self.check_for_checkmate(self.current_turn)


    def evaluate_move(self, from_pos, to_pos):
        score = 0
        # 1. Matériel
        captured_piece = self.pieces.get(tuple(to_pos))
        piece_values = {
            'pawn': 1,
            'knight': 3,
            'bishop': 3,
            'rook': 5,
            'queen': 9,
            'king': 0  # Le roi n'a pas de valeur car sa capture signifie la fin du jeu
        }

        if captured_piece:
            captured_piece_value = piece_values[captured_piece.split('_')[1]]
            score += captured_piece_value * 2  # Capturer une pièce vaut double sa valeur

        # 2. Contrôle du centre
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        if tuple(to_pos) in center_squares:
            score += 1  # Contrôler une case centrale vaut 1 point

        # 4. Développement des pièces
        piece = self.pieces[tuple(from_pos)]
        if piece.split('_')[1] in ['knight', 'bishop']:
            if from_pos[1] == 1 and piece.split('_')[0] == 'white':
                score += 1  # Développer une pièce mineure au début du jeu vaut 1 point
            if from_pos[1] == 6 and piece.split('_')[0] == 'black':
                score += 1  # Développer une pièce mineure au début du jeu vaut 1 point

        # 5. Possibilité de mise en échec
        original_piece = self.pieces.get(tuple(to_pos))
        self.pieces[tuple(to_pos)] = self.pieces.pop(tuple(from_pos))
        if self.check_for_check("black" if self.current_turn == "white" else "white"):
            score += 3  # Mettre le roi adverse en échec vaut 3 points
            if self.check_for_checkmate("black" if self.current_turn == "white" else "white"):
                score += 10  # Mettre le roi adverse en échec et mat vaut 10 points
        self.pieces[tuple(from_pos)] = self.pieces.pop(tuple(to_pos))
        if original_piece:
            self.pieces[tuple(to_pos)] = original_piece

        return score

    def promote_pawn(self, position):
        if self.current_turn != self.player_color:  # Promotion automatique à la dame pour l'IA
            self.pieces[position] = f"{self.current_turn}_queen"
            self.refresh_board()
            return

        promotion_window = tk.Toplevel(self)
        promotion_window.title("Promote Pawn")
        promotion_window.geometry("350x100")

        label = tk.Label(promotion_window, text="Choose a piece to promote to:")
        label.pack(pady=5)

        def promote(piece_type):
            color = self.current_turn
            self.pieces[position] = f"{color}_{piece_type}"
            self.refresh_board()
            promotion_window.destroy()

        pieces = ["queen", "rook", "bishop", "knight"]
        for piece in pieces:
            button = tk.Button(promotion_window, text=piece.capitalize(), command=lambda p=piece: promote(p))
            button.pack(pady=2, padx=5, side=tk.LEFT)

        # Empêche l'IA de jouer pendant la promotion du joueur
        self.wait_window(promotion_window)


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
        self.pieces[tuple(position)] = piece
        self.refresh_board()

    def update_selection_rectangle(self, offset_x=None, offset_y=None):
        if self.selection_rectangle:
            self.canvas.delete(self.selection_rectangle)
        if self.selected_position and self.current_turn == self.player_color:
            if offset_x is None:
                offset_x = (self.canvas.winfo_width() - self.columns * self.size) / 2
            if offset_y is None:
                offset_y = (self.canvas.winfo_height() - self.rows * self.size) / 2
            col, row = self.selected_position
            if self.player_color == "black":
                col = self.columns - 1 - col
                row = self.rows - 1 - row
            x1 = offset_x + col * self.size
            y1 = offset_y + row * self.size
            self.selection_rectangle = self.canvas.create_rectangle(x1, y1, x1 + self.size, y1 + self.size,
                                                                    outline="yellow", width=3)

    def Calculate_moves(self, piece, position, checking_for_castling=False):
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

                # Check for castling moves
                piece_color = piece.split("_")[0]
                if not checking_for_castling and not self.kings_moved[piece_color]:
                    if piece_color == "white":
                        row = 7
                        if not self.rooks_moved[piece_color]['left'] and all((i, row) not in self.pieces for i in range(1, 4)):
                            if not self.check_positions_for_attack(piece_color, [(4, row), (2, row), (3, row)]):
                                positions_available.append((2, row))  # Queen side castling
                        if not self.rooks_moved[piece_color]['right'] and all((i, row) not in self.pieces for i in range(5, 7)):
                            if not self.check_positions_for_attack(piece_color, [(4, row), (5, row), (6, row)]):
                                positions_available.append((6, row))  # King side castling
                    else:
                        row = 0
                        if not self.rooks_moved[piece_color]['left'] and all((i, row) not in self.pieces for i in range(1, 4)):
                            if not self.check_positions_for_attack(piece_color, [(4, row), (2, row), (3, row)]):
                                positions_available.append((2, row))  # Queen side castling
                        if not self.rooks_moved[piece_color]['right'] and all((i, row) not in self.pieces for i in range(5, 7)):
                            if not self.check_positions_for_attack(piece_color, [(4, row), (5, row), (6, row)]):
                                positions_available.append((6, row))  # King side castling

                for pos in positions_available:
                    if pos[0] < 0 or pos[0] >= 8 or pos[1] < 0 or pos[1] >= 8:
                        continue
                    else:
                        positions_available_valide.append(pos)
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
                        if tuple(move) in self.pieces and self.pieces[tuple(move)].split("_")[0] != piece.split("_")[0]:
                            positions_available.append(move)

                for pos in positions_available:
                    if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7:
                        continue
                    else:
                        positions_available_valide.append(pos)
            case _:
                print("Invalid piece name")
        return positions_available_valide

    def validMoves(self, piece, position, calculateMoves: list) -> list:
        valid_moves = []
        piece_color = piece.split("_")[0]
        piece_name = piece.split("_")[1]

        def is_clear_path(start, end, step):
            current = (start[0] + step[0], start[1] + step[1])
            while current != end:
                if tuple(current) in self.pieces:
                    return False
                current = (current[0] + step[0], current[1] + step[1])
            return True

        for move in calculateMoves:
            if piece_name in ["rook", "queen"]:
                if move[0] == position[0]:  # Vertical move
                    step = (0, 1) if move[1] > position[1] else (0, -1)
                    if is_clear_path(position, move, step):
                        if tuple(move) in self.pieces:
                            if self.pieces[tuple(move)].split("_")[0] != piece_color:
                                valid_moves.append(move)
                        else:
                            valid_moves.append(move)
                elif move[1] == position[1]:  # Horizontal move
                    step = (1, 0) if move[0] > position[0] else (-1, 0)
                    if is_clear_path(position, move, step):
                        if tuple(move) in self.pieces:
                            if self.pieces[tuple(move)].split("_")[0] != piece_color:
                                valid_moves.append(move)
                        else:
                            valid_moves.append(move)
            if piece_name in ["bishop", "queen"]:
                step_x = 1 if move[0] > position[0] else -1
                step_y = 1 if move[1] > position[1] else -1
                if abs(move[0] - position[0]) == abs(move[1] - position[1]):  # Diagonal move
                    if is_clear_path(position, move, (step_x, step_y)):
                        if tuple(move) in self.pieces:
                            if self.pieces[tuple(move)].split("_")[0] != piece_color:
                                valid_moves.append(move)
                        else:
                            valid_moves.append(move)
            elif piece_name == "pawn":
                direction = -1 if piece_color == "white" else 1
                start_row = 6 if piece_color == "white" else 1

                if tuple(move) not in self.pieces:
                    if move[0] == position[0]:  # Forward move
                        if move[1] == position[1] + direction:  # One step forward
                            valid_moves.append(move)
                        elif (move[1] == position[1] + 2 * direction and
                              position[1] == start_row and
                              (position[0], position[1] + direction) not in self.pieces):
                            valid_moves.append(move)
                elif tuple(move) in self.pieces and self.pieces[tuple(move)].split("_")[0] != piece_color:
                    if move in [(position[0] + 1, position[1] + direction),
                                (position[0] - 1, position[1] + direction)]:
                        valid_moves.append(move)
            elif piece_name == "knight":
                if tuple(move) not in self.pieces or self.pieces[tuple(move)].split("_")[0] != piece_color:
                    valid_moves.append(move)
            elif piece_name == "king":
                if tuple(move) in self.pieces:
                    if self.pieces[tuple(move)].split("_")[0] != piece_color:
                        valid_moves.append(move)
                else:
                    valid_moves.append(move)

        return valid_moves

    def check_positions_for_attack(self, color, positions):
        opponent_color = "white" if color == "black" else "black"
        for pos in positions:
            for piece_pos, piece in self.pieces.items():
                if piece.split("_")[0] == opponent_color:
                    moves = self.Calculate_moves(piece, piece_pos, checking_for_castling=True)
                    if tuple(pos) in self.validMoves(piece, piece_pos, moves):
                        return True
        return False

    def check_for_check(self, color):
        # Find the position of the king of the given color
        king_position = None
        for pos, piece in self.pieces.items():
            if piece == f"{color}_king":
                king_position = pos
                break
        if not king_position:
            return False

        # Check if any of the opponent's pieces can move to the king's position
        opponent_color = "white" if color == "black" else "black"
        for pos, piece in self.pieces.items():
            if piece.split("_")[0] == opponent_color:
                moves = self.Calculate_moves(piece, pos)
                if tuple(king_position) in self.validMoves(piece, pos, moves):
                    return True
        return False

    def check_for_checkmate(self, color):
        # Check if the player is in checkmate
        if not self.check_for_check(color):
            return False

        pieces_copy = list(self.pieces.items())  # Create a copy of the items to avoid RuntimeError

        for pos, piece in pieces_copy:
            if piece.split("_")[0] == color:
                valid_moves = self.validMoves(piece, pos, self.Calculate_moves(piece, pos))
                for move in valid_moves:
                    original_piece = self.pieces.get(tuple(move))
                    self.pieces[tuple(move)] = self.pieces.pop(tuple(pos))
                    if not self.check_for_check(color):
                        self.pieces[tuple(pos)] = self.pieces.pop(tuple(move))
                        if original_piece:
                            self.pieces[tuple(move)] = original_piece
                        return False
                    self.pieces[tuple(pos)] = self.pieces.pop(tuple(move))
                    if original_piece:
                        self.pieces[tuple(move)] = original_piece

        return True

    def check_for_stalemate(self, color):
        if self.check_for_check(color):
            return False  # Pas de pat si le joueur est en échec

        for pos, piece in self.pieces.items():
            if piece.split("_")[0] == color:
                valid_moves = self.validMoves(piece, pos, self.Calculate_moves(piece, pos))
                if valid_moves:
                    return False  # Pas de pat si le joueur a des mouvements valides

        return True  # Pat si aucune pièce du joueur n'a de mouvements valides

    def check_for_insufficient_material(self):
        remaining_pieces = list(self.pieces.values())
        if len(remaining_pieces) == 2:
            return True  # Roi contre roi

        if len(remaining_pieces) == 3:
            piece_types = [piece.split("_")[1] for piece in remaining_pieces]
            if "king" in piece_types and ("bishop" in piece_types or "knight" in piece_types):
                return True  # Roi et fou ou roi et cavalier contre roi

        if len(remaining_pieces) == 4:
            piece_types = [piece.split("_")[1] for piece in remaining_pieces]
            if piece_types.count("bishop") == 2:
                return True  # Roi et deux fous de couleurs opposées contre roi

        return False

    def check_for_draw(self, color):
        if self.check_for_stalemate(color):
            self.show_draw_message("Pat")
            return True

        if self.check_for_insufficient_material():
            self.show_draw_message("Matériel insuffisant")
            return True

        return False
    
    def analyze_csv(self):
        df = pd.read_csv(self.csv_file)
        similar_games = []

        current_moves = self.moves_of_game[self.current_turn]

        for index, row in df.iterrows():
            moves = ast.literal_eval(row["Moves"])
            player_color = row["Player Color"]
            ia_color = row["IA Color"]
            result = row["Result"]

            match_count = 0
            for move1, move2 in zip(moves[self.current_turn], current_moves):
                if move1["Move"] == move2["Move"]:
                    match_count += 1
                else:
                    break

            if match_count > 0:
                similar_games.append((match_count, moves, result))

        return similar_games

    def adjust_move_evaluation(self, similar_games):
        evaluation_adjustments = {}
        for match_count, moves, result in similar_games:
            for move_data in moves[self.current_turn][match_count:]:
                move = tuple(move_data["Move"])
                value = move_data["Value"]

                if move not in evaluation_adjustments:
                    evaluation_adjustments[move] = 0

                if result == "1-0" and self.current_turn == "white":
                    evaluation_adjustments[move] += value
                elif result == "0-1" and self.current_turn == "black":
                    evaluation_adjustments[move] += value
                else:
                    evaluation_adjustments[move] -= value

        return evaluation_adjustments

    def show_draw_message(self, reason):
        message = f"Égalité due à {reason}!"
        tk.messagebox.showinfo("Jeu Terminé", message)
        self.reset_board()
        self.controller.show_frame("MainMenu")

    def show_checkmate_message(self, winner_color):
        winner = "White" if winner_color == "white" else "Black"
        message = f"Checkmate! {winner} wins!"
        tk.messagebox.showinfo("Game Over", message)
        winnerRecord = "1-0" if winner == "White" else "0-1"
        self.record_game(self.moves_of_game, winnerRecord)
        self.reset_board()
        self.controller.show_frame("MainMenu")

    def return_to_main_menu(self):
        self.pack_forget()
        self.main_menu.pack(side="top", fill="both", expand=True)

    def reset_board(self):
        self.pieces.clear()
        self.selected_piece = None
        self.selected_position = None
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.selection_rectangle = None
        self.player_color = random.choice(["white", "black"])
        self.current_turn = "white"
        self.calculated_moves = np.array([])
        self.white_points = 0
        self.black_points = 0
        for widget in self.white_captures_frame.winfo_children():
            widget.destroy()
        for widget in self.black_captures_frame.winfo_children():
            widget.destroy()
        self.white_points_label.config(text="")
        self.black_points_label.config(text="")
        self.add_pieces()
        self.refresh_board()
