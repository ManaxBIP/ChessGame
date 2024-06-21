import tkinter as tk
import socket
import threading

class JoinMatch(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = tk.Label(self, text="Join Match", font=("Helvetica", 24))
        self.label.pack(pady=20)

        """ for server in servers:
            self.server_ip_label = tk.Label(self, text="Server IP:")
            self.server_ip_label.pack()
            self.server_ip_entry = tk.Entry(self)
            self.server_ip_entry.pack(pady=5)
        
            self.connect_button = tk.Button(self, text="Connect", font=("Helvetica", 14), command=self.connect_to_server)
            self.connect_button.pack(pady=20)
 """
        self.back_button = tk.Button(self, text="Back", font=("Helvetica", 14), command=self.go_back)
        self.back_button.pack(pady=20)

    def connect_to_server(self):
        server_ip = self.server_ip_entry.get()
        self.client_thread = threading.Thread(target=self.client, args=(server_ip,))
        self.client_thread.start()

    def go_back(self):
        self.controller.show_frame("MultiplayerMenu")

    def client(self, server_ip):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_ip, 5555))
        print(f"Connected to server at {server_ip}")

        while True:
            message = input("Your move: ")
            client.send(message.encode())
            response = client.recv(1024).decode()
            print(f"Server response: {response}")
