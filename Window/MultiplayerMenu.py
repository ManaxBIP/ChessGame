import tkinter as tk
import socket
import threading
from tkinter import messagebox

class MultiplayerMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = tk.Label(self, text="Multiplayer", font=("Helvetica", 24))
        self.label.pack(pady=20)

        self.create_button = tk.Button(self, text="Create Match", font=("Helvetica", 14), command=self.create_match)
        self.create_button.pack(pady=20)

        self.join_button = tk.Button(self, text="Join Match", font=("Helvetica", 14), command=self.join_match)
        self.join_button.pack(pady=20)

        self.back_button = tk.Button(self, text="Back", font=("Helvetica", 14), command=self.go_back)
        self.back_button.pack(pady=20)

    def create_match(self):
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.start()
        messagebox.showinfo("Server", "Server started. Waiting for players to join.")
        # Optionally, navigate to the game screen
        # self.controller.show_frame("ChessBoard")

    def join_match(self):
        self.controller.show_frame("JoinMatch")

    def go_back(self):
        self.controller.show_frame("MainMenu")

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", 5555))
        server.listen(2)
        print("Server started. Waiting for connections...")

        while True:
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    print(f"Received: {message}")
                    # Handle the message and send response
            except:
                client_socket.close()
                break
