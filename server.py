import socket
import sys
from _thread import *

clients = list()
pubKeys = list()
messageSize = 1024
IP = '192.226.1.2'
PORT = 99

def remove(connection):
    connection.close()
    if(connection in clients):
        clients.remove(connection)

def removePubKeys(ip):
    for pubKey in pubKeys:
        if(pubKey['addr'] == ip):
            pubKeys.remove(pubKey)

def broadcast(message, sender):
    for client in clients:
        if(client['conn'] != sender):
            try:
                client['conn'].send(message.encode('utf-8'))
            except:
                remove(client['conn'])
                removePubKeys(client['addr'])

def clientConnection(conn, addr):
    # get public key
    data = conn.recv(messageSize)
    data = data.decode('utf-8')
    pubKey = eval(data)

    # send others public key to new client
    conn.send(str(pubKeys).encode('utf-8'))

    data = {
        'pubKey': pubKey,
        'addr': addr[0],
        'connected': False
    }

    pubKeys.append(data)

    # send new client's public key to other client
    data = {
        'type': 'pubkey',
        'message': {
            'addr': addr[0],
            'pubKey': pubKey,
            'connected': False
        }
    }
    broadcast(str(data), conn)

    while True:
        try:
            message = conn.recv(messageSize)
            message = message.decode('utf-8')
            ciphertext, length = message.split(',')
            if message:
                print(f"Sender: {addr[0]}")
                print(f"Message: {ciphertext}")
                print(f"Length: {length}\n")

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

        clients.append({
            'conn': conn,
            'addr': addr[0],
        })

        print(f"{addr[0]} is Connected")

        start_new_thread(clientConnection, (conn, addr))

    conn.close()
    server.close()