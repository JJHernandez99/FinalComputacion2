import socket,threading
from argumentos import parser
import tkinter 
from tkinter import messagebox
import os
import logging
import multiprocessing 

server = None
args=parser()
host_4 = '127.0.0.1'
host_6 = '::1'
port = args.port
clients_name = " "
clients = []
users = []
validated_users = []

#FRONT-END SERVER
#Ventana servidor
screen_servidor = tkinter.Tk()
screen_servidor.title("Server")
screen_servidor.configure(bg='#044f75')

#Ventana superior para conectarse al servidor
frame = tkinter.Frame(screen_servidor)
button_connect = tkinter.Button(frame, text="Conectarse", bg='#415d6b', command=lambda : start_server())
button_connect.pack(side=tkinter.LEFT)
button_stop = tkinter.Button(frame, text="Stop", bg='#415d6b', command=lambda : stop_server(), state=tkinter.DISABLED)
button_stop.pack(side=tkinter.LEFT)
frame.pack(side=tkinter.TOP, pady=(5, 0))

#Etiqueta para mostrar host y puerto del servidor
frame_connection = tkinter.Frame(screen_servidor, bg='#044f75')
label_host = tkinter.Label(frame_connection, text = "Host: ", bg='#044f75', font=('Arial', 14))
label_host.pack(side=tkinter.LEFT)
label_port = tkinter.Label(frame_connection, text = "Puerto: ", bg='#044f75', font=('Arial', 14))
label_port.pack(side=tkinter.LEFT)
frame_connection.pack(side=tkinter.TOP, pady=(5, 0))

# Ventana de clientes conectados al servidor
clientFrame = tkinter.Frame(screen_servidor, bg='#044f75')
label_users = tkinter.Label(clientFrame, text="Lista de usuarios conectados", bg='#044f75', font=('Arial', 18)).pack()
lista = tkinter.Text(clientFrame, height=20, width=35)
lista.pack()
lista.config(background="#FFFFFF", highlightbackground="#044f75", state="disabled")
clientFrame.pack(side=tkinter.BOTTOM, pady=(10, 20))

#Mutex para el manejo de log de clientes / conexiones 
def control_log():
    global lock_acceso_archivo_log
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler("logs.txt"),
            logging.StreamHandler()
        ]
    )
    
    lock_acceso_archivo_log.acquire() #Bloquea el uso del log
    logging.info(threading.current_thread().name)
    lock_acceso_archivo_log.release() #Libera el uso del log

lock_acceso_archivo_log = threading.Lock() #Se crea el bloqueo

def validate_username(name):
    usuarios_permitidos_path = "/home/jhernandez/Documentos/Universidad/FinalComputacion2/users.txt"
    if not os.path.isfile(usuarios_permitidos_path):
        return False

    with open(usuarios_permitidos_path, "r") as f:
        usuarios_permitidos = [line.strip() for line in f]

    if name not in usuarios_permitidos:
        return False

    return True

# función para validar el usuario a través de un proceso separado
def validate_username_process(name, result_queue):
    result_queue.put(validate_username(name))

#Funcion para arrancar el servidor
def start_server():
    button_connect.config(state=tkinter.DISABLED)
    button_stop.config(state=tkinter.NORMAL)

    # crear una cola compartida para pasar los resultados de validación del nombre de usuario
    result_queue = multiprocessing.Queue()
    
    # crear un proceso para validar los usuarios permitidos
    usuarios_permitidos_process = multiprocessing.Process(target=validate_username_process)
    usuarios_permitidos_process.start()

    print("PROCESO CORRIENDO VALIDACION - start server funcion")
    print(result_queue)

   # Crear sockets para IPv4 e IPv6
    server_ipv4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ipv6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    # Enlazar y escuchar en ambos sockets
    server_ipv4.bind((host_4, port))
    server_ipv6.bind((host_6, port))
    server_ipv4.listen()
    server_ipv6.listen()

    # Crear hilos para aceptar clientes en ambos sockets
    thread_ipv4 = threading.Thread(target=accept_clients, args=(server_ipv4," ",result_queue))
    thread_ipv4.start()

    thread_ipv6 = threading.Thread(target=accept_clients, args=(server_ipv6," ",result_queue))
    thread_ipv6.start()

    label_host["text"] = "Host: " + host_4
    label_port["text"] = "Port: " + str(port)

    #Log de arranque de servidor 
    hilo = threading.Thread(target=control_log, name='"---------- Servidor corriendo ----------"')
    hilo.start()

#Funcion para parar servidor
def stop_server():
    global server
    button_connect.config(state=tkinter.NORMAL)
    hilo = threading.Thread(target=control_log, name='"---------- Se paro el servidor----------"')
    hilo.start()
    button_stop.config(state=tkinter.DISABLED)

#Funcion para aceptar las conexiones de los clientes
def accept_clients(the_server, y,result_queue):
     while True:
        client, addr = the_server.accept()

        username = client.recv(4096).decode() #Tomo el nombre del usuario que ingresa
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=validate_username_process, args=(username, result_queue))
        process.start()
        print("PROCESO CORRIENDO VALIDACION - aceptar cliente funcion")
        print(result_queue)
        process.join()

        if not result_queue.get():
            error_msg = "Usuario no permitido. Desconectando..."
            client.send(error_msg.encode())
            client.close()
            #Log del error
            hilo = threading.Thread(target=control_log, name=f'"---- {error_msg} ---------"')
            hilo.start()
            continue

        clients.append(client)
        validated_users.append(username)

        thread = threading.Thread(target=handle_client, args=(client, addr, username))
        thread.start()

        #Log nuevo cliente 
        hilo = threading.Thread(target=control_log, name=f'"---- Se conecto un nuevo cliente al serivdor: {username} ---------"')
        hilo.start()

# Función para recibir mensaje del cliente actual y enviar ese mensaje a otros clientes
def handle_client(client_connection, addr, username):
    global server, clients, users, validated_users
    client_msg = " "
    validated = True

    # Mensaje de bienvenida
    welcome_msg = f"{username} te has unido al chat"
    client_connection.send(welcome_msg.encode())
    users.append(username)
    update_list(users)  #Actualizar nombre de usuarios en pantalla

    #Recorre en bloques 
    while True:
        try:
            data = client_connection.recv(500000).decode()
        except UnicodeDecodeError as eror:
            data = ""
        if not data: break
        if data == "/exit":
            print("Salio el usuario con exito")
            # Elimina el hilo del cliente
            for thread in threading.enumerate():
                if thread.name == f'Thread for {username}':
                    thread.join()

            # Agrega al archivo log que el cliente ha salido
            with open('logs.txt', 'a') as file:
                file.write(f'{username} ha salido del chat.\n')
            break

        if data == "/list":
            connected_clients = ", ".join(users)
            server_msg = "Usuarios conectados: " + connected_clients
            client_connection.send(server_msg.encode())

        if not validated:
            break
            
        client_msg = data

        if client_msg.startswith("Bytes:") :
            file_data = client_msg.split(" ")
            size = int(file_data[1])
            print("Se recibio un archivo con bytes " + file_data[1] + " con nombre: " + file_data[2])

            file_buffer = client_connection.recv(size)
            save_file(file_buffer, file_data[2])
            data = client_connection.recv(4096).decode()
            client_connection.send("Archivo enviado".encode())

        index = get_client(clients, client_connection)
        sending_client_name = users[index]

        
        #Se envia x cada cliente
        for i in clients:
            if i != client_connection:
                server_msg = str(sending_client_name + "-> " + client_msg)
                i.send(server_msg.encode())

                #Log msg de cada cliente 
                hilo = threading.Thread(target=control_log, name=server_msg)
                hilo.start()    

    index = get_client(clients, client_connection)
    del users[index] #Elimino el cliente del server
    del clients[index] #Elimino el cliente de la conexion
    server_msg = "BYE!"
   
    client_connection.send(server_msg.encode())
    client_connection.close()

    update_list(users)  #Actualizar nombre de usuarios en pantalla

#Devuelve el índice del cliente actual en la lista de clientes
def get_client(client_list, curr_client):
    index = 0
    for conexion in client_list:
        if conexion == curr_client:
            break
        index = index + 1
    return index

#Funcion para actualizar lista de usuarios en el servidor
def update_list(list_users):
    lista.config(state=tkinter.NORMAL)
    lista.delete('1.0', tkinter.END)

    for i in list_users:
        lista.insert(tkinter.END, i +"\n")
    lista.config(state=tkinter.DISABLED)

#Agrego a la carpeta files los archivos enviados por los clientes
def save_file(data, name):
    data_b = bytearray(data)
    path_result = os.getcwd() + "/files/" + name
    f = open(path_result, 'wb')
    f.write(data_b)
    f.close()



screen_servidor.mainloop()