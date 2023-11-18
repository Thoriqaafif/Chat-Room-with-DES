# Python program to implement client side of chat room. 
import socket 
import select 
import sys 

IP = '192.168.1.13'
Port = 99

if __name__ == "__main__":
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.connect((IP, Port))

	while True:
		sockets_list = [sys.stdin, server]

		read_sockets,write_socket, error_socket = select.select(sockets_list,[],[]) 

		for socks in read_sockets: 
			if socks == server: 
				message = socks.recv(2048) 
				print (message.decode('utf-8')) 
			else: 
				message = input()
				server.send(message.encode('utf-8'))  
				sys.stdout.write("<You>") 
				sys.stdout.write(message) 
				sys.stdout.flush() 
	server.close()