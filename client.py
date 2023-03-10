import socket, threading
from argumentos import parser
import tkinter 
from tkinter import filedialog
import os 

# Conexion Cliente
client = None
args=parser()
host='127.0.0.1'
port=args.port
name = args.name

def connect_to_server(name):
    global client, port, host
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        client.send(name.encode()) # Enviar nombre de usuario al servidor después de conectar

        name_user.config(state=tkinter.DISABLED)
        button_connect.config(state=tkinter.DISABLED)
        msg.config(state=tkinter.NORMAL)

        # inicia un hilo para seguir recibiendo mensajes del servidor
        threading._start_new_thread(client_receive, (client, "m")) 
        # thread = threading.Thread(target=client_receive, args=(client,"m")) ## REVISAR
        # thread.start()
    except Exception as e:
        tkinter.messagebox.showerror(title="ERROR!!!", message="Servidor inaccesible")

#Conexion con el servidor
def connect():
    global username, client
    if len(name_user.get()) < 1:
        tkinter.messagebox.showerror(title="ERROR!!!", message="Ingrese su nombre !!!")
    else:
        username = name_user.get()
        connect_to_server(username)

#Cargar archivos y leerlo ## REVISAR
def upload_file(frame):
    file = filedialog.askopenfile(parent=frame,mode='rb',title='Choose a file')
    if file != None:
        file_name = os.path.basename(str(file.name))
        
        print(file_name)

        data = file.read()       
        send_file(data,file_name)
        file.close()
        print("Tiene %d bytes el archivo." % len(data))


#Recive los mensaje enviados al server para mostrar
def client_receive(socket,m):
    while True:
        from_server = socket.recv(4096).decode()
        if not from_server: break
        #Muestra por pantalla mensaje del servidor
        texts = chat.get("1.0", tkinter.END).strip()
        chat.config(state=tkinter.NORMAL)
        if len(texts) < 1:
            chat.insert(tkinter.END, from_server)
        else:
            chat.insert(tkinter.END, "\n\n"+ from_server)

        chat.config(state=tkinter.DISABLED)
        chat.see(tkinter.END)
    
    socket.close()
    screen_cliente.destroy() 

#Funcion de enviar mensajes (cliente)
def client_send(message):
    message = message.replace('\n', '')
    texts = chat.get("1.0", tkinter.END).strip()
    
    # habilitar pantalla de visualización e insertar el texto y luego deshabilitar.
    chat.config(state=tkinter.NORMAL)
    if len(texts) < 1:
        chat.insert(tkinter.END, "-> "+ " " + message, "mensaje")
    else:
        chat.insert(tkinter.END, "\n\n" + "-> "+ " " + message, "mensaje")

    #Desabilitar pantalla de visualizacion para insertar texto
    chat.config(state=tkinter.DISABLED)

    send_message(message)

    chat.see(tkinter.END)
    msg.delete('1.0', tkinter.END)

#Enviar mensaje al server
def send_message(message):
    client_msg = str(message)
    client.send(client_msg.encode())
    if message == "exit":
        client.close()
        screen_cliente.destroy()
    print("Mensaje enviado")

#Enviar archivos al server ##REVISAR
def send_file(file,file_name):
    client.send("Bytes: {} {}".format(len(file) ,file_name).encode())
    client.send(file)
    client.send("termino".encode())
    print("Se envio al server el archivo")

#FRONT-END CLIENTE
#Ventana cliente
screen_cliente = tkinter.Tk()
screen_cliente.title("Cliente")
username = " "
screen_cliente.configure(bg='#044f75')

#Ventana superior para ingresar nombre de usuario y conectarse al server
frame_user = tkinter.Frame(screen_cliente, bg='#044f75')
label_name = tkinter.Label(frame_user, text = "Nombre de usuario:", bg='#044f75').pack(side=tkinter.LEFT)
name_user = tkinter.Entry(frame_user, bg='#ffffff')
name_user.pack(side=tkinter.LEFT)
button_connect = tkinter.Button(frame_user, text="Conectarse", bg='#415d6b', padx=10, command=lambda : connect())
button_connect.pack(side=tkinter.LEFT)
frame_user.pack(side=tkinter.TOP)

#Ventana Chat
screen_chat = tkinter.Frame(screen_cliente, bg='#044f75')
label_title = tkinter.Label(screen_chat, text="CHAT", bg='#044f75').pack()
scroll = tkinter.Scrollbar(screen_chat, bg='#415d6b')
scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
chat = tkinter.Text(screen_chat, height=35, width=50)
chat.pack()
chat.tag_config("mensaje")
scroll.config(command=chat.yview)
chat.config(yscrollcommand=scroll.set, background="#F4F6F7", highlightbackground="blue", state="disabled")
screen_chat.pack(side=tkinter.TOP)

#Ventana para enviar mensajes y archivos
bottomFrame = tkinter.Frame(screen_cliente, bg='#415d6b')
msg = tkinter.Text(bottomFrame, height=2, width=30)
msg.pack(side=tkinter.LEFT)
msg.config(highlightbackground="grey", state="disabled")
msg.bind("<Return>", (lambda event: client_send(msg.get("1.0", tkinter.END))))
upload_button = tkinter.Button(bottomFrame, text="Subir archivo", command=(lambda: upload_file(bottomFrame)))
upload_button.pack(side=tkinter.LEFT)
bottomFrame.pack(side=tkinter.BOTTOM, padx=5)

screen_cliente.mainloop()