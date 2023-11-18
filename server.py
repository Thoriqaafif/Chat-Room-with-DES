import socket
import sys
from _thread import *

clients = list()
messageSize = 1024
IP = '192.168.1.13'
PORT = 99

def remove(connection):
    connection.close()
    if(connection in clients):
        clients.remove(connection)

def broadcast(message, sender):
    for client in clients:
        if(client != sender):
            try:
                client.send(message.encode('utf-8'))
            except:
                remove(client)

def clientConnection(conn, addr):
    while True:
        try:
            message = conn.recv(messageSize)
            if message:
                print(f"Sender: {addr[0]}")
                print(f"Message: {message.decode('utf-8')}")

                broadcast(f"{addr[0]},{message}", conn)
            
            else:
                remove(conn)
        except:
            continue

if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((IP, PORT))
    server.listen(50)

    # server accept connection request from each client
    while True:
        conn, addr = server.accept()
        clients.append(conn)

        print(f"{addr[0]} is Connected")

        start_new_thread(clientConnection, (conn, addr))

    conn.close()
    server.close()