import socket
import os

# codigo para hacer codificacion
from datetime import datetime

key = 99


def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day


def decode_image(name):
    dirpath = os.getcwd()
    path = dirpath + '/' + name + '.enc'
    path_result = dirpath + '/' + 'result-' + to_integer(datetime.datetime.utcnow().timestamp()) + name
    # print path of image file and decryption key that we are using
    print('The path of file : ', path)
    print('Note : Encryption key and Decryption key must be same.')
    print('Key for Decryption : ', key)

    # open file for reading purpose
    fin = open(path, 'rb')

    # storing image data in variable "image"
    image = fin.read()
    fin.close()

    # converting image into byte array to perform decryption easily on numeric data
    image = bytearray(image)

    # performing XOR operation on each value of bytearray
    for index, values in enumerate(image):
        image[index] = values ^ key

    # opening file for writing purpose
    fin = open(path_result, 'wb')

    # writing decryption data in image
    fin.write(image)
    fin.close()
    print('Decryption Done...')
    return path_result


def encode_image(data, name):
    dirpath = os.getcwd()
    path_result = dirpath + '/' + name + '.enc'
    image = bytearray(data)

    # performing XOR operation on each value of bytearray
    for index, values in enumerate(image):
        image[index] = values ^ key

    # opening file for writing purpose
    fin = open(path_result, 'wb')

    # writing encrypted data in image
    fin.write(image)
    fin.close()
    print('Encryption Done...')


def server_program():
    buffer_size = 4096
    wait_for_image = False
    basename = ""
    # get the hostname
    host = socket.gethostname()
    port = 5000  # initiate port no above 1024
    print("init server")
    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(2)
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address))
    while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        if wait_for_image:
            print("esperando por la imagen")
            data = conn.recv(buffer_size)
            if data:
                print("imagen obtenida: " + str(data))
                # encriptar imagen
                encode_image(data, basename)
                wait_for_image = False
                msg = "Imagen get it"
                conn.send(msg.encode())
                # conn.close()
                break

        data = conn.recv(1024).decode()
        if data.startswith("get image"):
            print("Need get image")

        if data.startswith("SIZE"):
            tmp = data.split()
            size = int(tmp[1])
            basename = tmp[2]

            print('got size')
            print('size is' + str(size))
            print('name get it: ' + basename)
            msg = "GOT SIZE"
            conn.send(msg.encode())
            # Now set the buffer size for the image
            buffer_size = size
            wait_for_image = True
            continue
        if not data:
            # if data is not received break
            break
        print("from connected user: " + str(data))
        data = input(' -> ')
        conn.send(data.encode())  # send data to the client
    print("termino")
    conn.close()  # close the connection


if __name__ == '__main__':
    server_program()
