import socket, threading
from argumentos import parser
import threading
import socket

args=parser()
port=args.port
name = args.name
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', port))


def client_receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == "Nombre de usuario":
                client.send(name.encode('utf-8'))
            else:
                print(message)
        except:
            print('Error!')
            client.close()
            break


def client_send():
    while True:
        message = f'{name}: {input("->")}'
        client.send(message.encode('utf-8'))


receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()