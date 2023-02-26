import socket
import os
import sys


# funcion para guardar archivos recibidos por el servidor
def get_file_data(t_size, client_socket):
    tmp = t_size.split()
    size = int(tmp[2])
    basename = tmp[3]
    dirpath = os.getcwd()
    print('got size')
    print('size is' + str(size))
    print('name get it: ' + basename)
    client_socket.send("GOT CONFIRMATION".encode())
    data = client_socket.recv(size)
    path_save = dirpath + '/' + basename
    print("path_save: " + path_save)
    fin = open(path_save, 'wb')

    # writing decryption data in image
    fin.write(data)
    fin.close()
    print('Save file Done...')
    msg = "-FILE GET IT-"
    client_socket.send(msg.encode())


# funcion encargada para entender y parsear comandoss
def check_image_command(message, client_socket):
    if message.startswith("SIZE FILE"):
        get_file_data(message, client_socket)
        return
    if message.startswith("up file"):
        dirpath = os.getcwd()
        commands = message.split("up file")
        image = commands[1].strip()
        if image == "":
            print("witout parameter")
            return
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
        print("image send")


# programa principal de cliente
def client_program():
    # se obtienen los argumentos
    print("Arguments count: " + str(len(sys.argv)))
    # se setea e
    host = socket.gethostname()  # host de donde se conecta
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000  # se setea el puerto desde argumento o por defecto

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    message = input(" -> ")  # take input
    check_image_command(message, client_socket)

    while message.lower().strip() != 'bye':
        print("inicia loop")
        client_socket.send(message.encode())  # send message
        data = client_socket.recv(1024).decode()  # receive response
        print('Received from server: ' + data)  # show in terminal
        check_image_command(data, client_socket)
        message = input(" -> ")  # again take input
        check_image_command(message, client_socket)

    client_socket.close()  # close the connection
    print('termino')


if __name__ == '__main__':
    client_program()
