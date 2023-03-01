import socket, threading
from argumentos import parser
import threading
import socket

args=parser()
host = '127.0.0.1'
port = args.port
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
clients = []
users = []

#Manejo de mensajes
def broadcast(message):
    for client in clients:
        client.send(message)

#Manejo de conexiones de los clientes
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            name = users[index]
            
            broadcast(f'{name} ha salido del chat!'.encode('utf-8'))
            users.remove(name)
            break

#Funcion para aceptar las conexiones de los clients
def accept_clients():
    print('SERVER')
    while True:
        
        client, address = server.accept()
        print(f'Conexion establecida por: {str(address)}')
        client.send('Nombre de usuario'.encode('utf-8'))
        name = client.recv(1024)
        users.append(name)
        clients.append(client)
        print(f'Nombre de usuario: {name}'.encode('utf-8'))
        
        broadcast(f'{name} se conecto al chat'.encode('utf-8'))
        client.send('Estas conectado!'.encode('utf-8'))
        
        
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


if __name__ == "__main__":
    accept_clients()