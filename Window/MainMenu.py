import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = tk.Label(self, text="ChessGame", font=("Helvetica", 24))
        self.label.pack(pady=20)

        self.play_button = tk.Button(self, text="Play vs IA", font=("Helvetica", 14), command=self.start_game)
        self.play_button.pack(pady=20)

        self.play_ia_vs_ia_button = tk.Button(self, text="IA vs IA", font=("Helvetica", 14), command=self.start_ia_vs_ia)
        self.play_ia_vs_ia_button.pack(pady=20)

        self.stats_button = tk.Button(self, text="Statistiques", font=("Helvetica", 14), command=self.show_statistics)
        self.stats_button.pack(pady=20)

    def start_game(self):
        chess_board_frame = self.controller.frames["ChessBoard"]
        chess_board_frame.reset_board()
        chess_board_frame.set_mode("player_vs_ia")
        self.controller.show_frame("ChessBoard")

    def start_ia_vs_ia(self):
        chess_board_frame = self.controller.frames["ChessBoard"]
        chess_board_frame.reset_board()
        chess_board_frame.set_mode("ia_vs_ia")
        self.controller.show_frame("ChessBoard")
        chess_board_frame.start_ia_vs_ia_game()

    def show_statistics(self):
        # Create a new window for displaying statistics
        stats_window = tk.Toplevel(self)
        stats_window.title("Statistiques des Parties")

        # Read the CSV file
        df = pd.read_csv("chess_game_data.csv")

        # Calculate statistics
        total_games = len(df)
        wins_by_color = df['Result'].value_counts()

        # Map result to more descriptive labels
        wins_by_color.index = wins_by_color.index.map({'1-0': 'White Wins', '0-1': 'Black Wins'})

        # Create a figure for plotting
        fig = Figure(figsize=(6, 8))

        # Plot 1: Total games played
        ax1 = fig.add_subplot(211)
        ax1.bar(['Total Games'], [total_games], color=['orange'])
        ax1.set_title('Total Games Played')

        # Add space between the two plots
        fig.subplots_adjust(hspace=0.5)

        # Plot 2: Wins by color
        ax2 = fig.add_subplot(212)
        ax2.bar(wins_by_color.index, wins_by_color.values, color=['black', 'grey'])
        ax2.set_title('Wins by Color')

        # Create a canvas to display the figure
        canvas = FigureCanvasTkAgg(fig, master=stats_window)
        canvas.draw()
        canvas.get_tk_widget().pack()
