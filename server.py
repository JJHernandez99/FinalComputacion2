from argumentos import parser
from tkinter import messagebox, ttk
from ttkthemes import ThemedTk
from multiprocessing import Process, Queue
import tkinter 
import os
import socket,threading
import logging

#FRONT-END SERVER
#Ventana servidor
screen_servidor = ThemedTk(theme="arc")
screen_servidor.title("Server")
screen_servidor.configure(bg='#f0f0f0')

# Configuración de estilo para ttk widgets
style = ttk.Style()
style.configure("TButton", foreground="#000", background="#90AFC5", font=("Arial", 12))

#Ventana superior para conectarse al servidor
frame = ttk.Frame(screen_servidor)
button_connect = ttk.Button(frame, text="Conectarse", command=lambda : start_server())
button_connect.pack(side=tkinter.LEFT, padx=5)
button_stop = ttk.Button(frame, text="Stop", command=lambda : stop_server(), state=tkinter.DISABLED)
button_stop.pack(side=tkinter.LEFT, padx=5)
frame.pack(side=tkinter.TOP, pady=(10, 0))

#Etiqueta para mostrar host y puerto del servidor
frame_connection = ttk.Frame(screen_servidor)
label_host = ttk.Label(frame_connection, text = "Host: ", font=('Arial', 14))
label_host.pack(side=tkinter.LEFT, padx=5)
label_port = ttk.Label(frame_connection, text = "Puerto: ", font=('Arial', 14))
label_port.pack(side=tkinter.LEFT, padx=5)
frame_connection.pack(side=tkinter.TOP, pady=(10, 0))

# Ventana de clientes conectados al servidor
clientFrame = ttk.Frame(screen_servidor)
label_users = ttk.Label(clientFrame, text="Lista de usuarios conectados", font=('Arial', 18))
label_users.pack(pady=5)
lista = tkinter.Text(clientFrame, height=20, width=35, bg='#ECECEC')
lista.pack(pady=5)
lista.config(highlightbackground="#90AFC5", state="disabled")
clientFrame.pack(side=tkinter.BOTTOM, pady=(10, 20))

#Declaracion de variables
server = None
args=parser()
port = args.port
clients_name = " "
clients = []
users = []
validated_users = []
server_socket = None

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

# Función para validar el nombre de usuario
def validate_username(name):
    usuarios_permitidos_path = os.path.dirname(__file__)+"/users.txt"
    if not os.path.isfile(usuarios_permitidos_path):
        return False

    with open(usuarios_permitidos_path, "r") as f:
        usuarios_permitidos = [line.strip() for line in f]

    if name not in usuarios_permitidos:
        return False

    return True

# Función que ejecuta el proceso de validación de usuario de forma continua
def validate_username_process(result_queue):
    while True:
        username = result_queue.get()  # Esperar a recibir un nombre de usuario
        result = validate_username(username)
        result_queue.put(result)  # Devolver el resultado de la validación

#Funcion para arrancar el servidor
def start_server():
    global server_socket
    button_connect.config(state=tkinter.DISABLED)
    button_stop.config(state=tkinter.NORMAL)
    
    # cola compartida para pasar los nombres de usuario a validar y recibir los resultados
    result_queue = Queue()

    # proceso para validar los usuarios permitidos
    usuarios_permitidos_process = Process(target=validate_username_process, args=(result_queue,))
    usuarios_permitidos_process.start()

    print("PROCESO CORRIENDO VALIDACION - start server funcion")
    print(result_queue)

    # Crear sockets para IPv4 e IPv6
    server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Enlazar y escuchar en ambos sockets
    server_socket.bind(('::', port))
    server_socket.listen()

    # Crear hilos para aceptar clientes en ambos sockets
    thread_server= threading.Thread(target=accept_clients, args=(server_socket," ",result_queue))
    thread_server.start()

    label_host["text"] = "Host: IPv4 / IPv6"
    label_port["text"] = "Port: " + str(port)

    #Log de arranque de servidor 
    hilo = threading.Thread(target=control_log, name='"---------- Servidor corriendo ----------"')
    hilo.start()

#Funcion para aceptar las conexiones de los clientes
def accept_clients(server_socket,y,result_queue):
     while True:
        client, addr = server_socket.accept()

        username = client.recv(4096).decode() #Tomo el nombre del usuario que ingresa
        
        # Enviar el nombre de usuario a través de la cola para validar
        result_queue.put(username)

        # Esperar el resultado de la validación
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
        hilo = threading.Thread(target=control_log, name=f'"---- Se conecto un nuevo cliente al serivdor: {username} - IP: {addr} ---------"')
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
            data = client_connection.recv(4096).decode()
        except UnicodeDecodeError as eror:
            data = ""
              
        if data == "/exit":

            client_connection.close()
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

                   
        client_msg = data

        if client_msg.startswith("Bytes:") :
            file_data = client_msg.split(" ")
            size = int(file_data[1])
            print("Se recibio un archivo con bytes " + file_data[1] + " con nombre: " + file_data[2])

            # Recibe el archivo en bloques de 4096 bytes
            file_buffer = b""
            remaining_bytes = size
            while remaining_bytes > 0:
                if remaining_bytes >= 4096:
                    block = client_connection.recv(4096)
                else:
                    block = client_connection.recv(remaining_bytes)
                file_buffer += block
                remaining_bytes -= len(block)

            save_file(file_buffer, file_data[2])
            client_connection.send("-> Archivo enviado".encode())
            continue

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
    del validated_users[index]
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

def stop_server():
    global server_socket
    button_connect.config(state=tkinter.NORMAL)
    hilo = threading.Thread(target=control_log, name='"---------- Se paro el servidor----------"')
    hilo.start()
    button_stop.config(state=tkinter.DISABLED)
    if server_socket:
        server_socket.close()
    screen_servidor.destroy()
    os._exit(0)

screen_servidor.mainloop()