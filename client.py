import socket
import os


def check_image_command(message, client_socket):
    if message.startswith("up image"):
        dirpath = os.getcwd()
        commands = message.split("up image")
        image = commands[1].strip()
        print("se va enviar imagen: *" + image + "*")
        path = dirpath + '/' + image
        with open(path, 'rb') as f:
            l = f.read()
            f.close()
            size = len(l)
            msg = "SIZE " + str(size) + " " + image
            client_socket.send(msg.encode())
            answer = client_socket.recv(1024).decode()
            print('answer = ' + answer)
            if answer == 'GOT SIZE':
                client_socket.sendall(l)
                # check what server send
                answer = client_socket.recv(1024).decode()
                print('answer = ' + answer)

    # client_socket.send(f.read())

        print("imagen enviada")


def client_program():
    host = socket.gethostname()  # as both code is running on same pc
    port = 5000  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    message = input(" -> ")  # take input
    check_image_command(message, client_socket)

    while message.lower().strip() != 'bye':
        client_socket.send(message.encode())  # send message
        data = client_socket.recv(1024).decode()  # receive response
        print('Received from server: ' + data)  # show in terminal

        message = input(" -> ")  # again take input
        check_image_command(message, client_socket)

    client_socket.close()  # close the connection
    print('termino')


if __name__ == '__main__':
    client_program()
