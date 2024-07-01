import socket
import threading
import random

clients = []
colors = ["white", "black"]

def broadcast(message, _client):
    for client in clients:
        if client != _client:
            try:
                client.send(message)
            except:
                client.close()
                clients.remove(client)

def handle_client(client, color):
    client.send(color.encode())
    while True:
        try:
            message = client.recv(1024)
            if not message:
                break
            broadcast(message, client)
        except:
            client.close()
            clients.remove(client)
            break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen()

    print("Server is listening...")

    while True:
        client, address = server.accept()
        print(f"Connected with {address}")
        clients.append(client)
        if len(clients) == 2:
            random.shuffle(colors)
            for c, color in zip(clients, colors):
                thread = threading.Thread(target=handle_client, args=(c, color))
                thread.start()
            for c in clients:
                c.send("start".encode())

if __name__ == "__main__":
    start_server()
