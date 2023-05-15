import socket, threading
from argumentos import parser
import tkinter 
from tkinter import filedialog, ttk
from ttkthemes import ThemedTk
import os
import tkinter.messagebox
from PIL import Image, ImageTk
from docx import Document

# Conexion Cliente
client = None
args=parser()
port=args.port
# name = args.name
ip = args.ip

def connect_to_server(name):
    global client, port, ip

    try:
        client_ipv6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        client_ipv6.connect((ip, port))
        print('Conexión exitosa a través de IPv6')
        client = client_ipv6  # Utiliza el socket IPv6 para la conexión
    except:
        print('No se pudo conectar a través de IPv6')

        try:
            client_ipv4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_ipv4.connect((ip, port))
            print('Conexión exitosa a través de IPv4')
            client = client_ipv4  # Utiliza el socket IPv4 para la conexión
        except:
            tkinter.messagebox.showerror(title="ERROR!!!", message="No se pudo conectar con el servidor")
            return

    client.send(name.encode()) # Enviar nombre de usuario al servidor después de conectar

    name_user.config(state=tkinter.DISABLED)
    button_connect.config(state=tkinter.DISABLED)
    msg.config(state=tkinter.NORMAL)

    # Creo hilos y lo lanzo
    thread = threading.Thread(target=client_receive, args=(client,"m"))
    thread.start()


#Conexion con el servidor
def connect():
    global username, client
    if len(name_user.get()) < 1:
        tkinter.messagebox.showerror(title="ERROR!!!", message="Ingrese su nombre !!!") 
    else:
        username = name_user.get()
        connect_to_server(username)

#Cargar archivos y leerlo
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

    
def view_file(frame):
    
    file_path = filedialog.askopenfilename(initialdir='/home/jhernandez/Documentos/Universidad/FinalComputacion2/files', title='Seleccione un archivo')
    _, file_extension = os.path.splitext(file_path)

    if file_extension.lower() == '.txt':
        with open(file_path, 'r') as file:
            content = file.read()

        # Crear una nueva ventana para mostrar el contenido del archivo
        window = tkinter.Toplevel()
        window.title(file_path)
        text = tkinter.Text(window)
        text.pack()
        text.insert(tkinter.END, content)

    elif file_extension.lower() in ['.jpg', '.jpeg', '.png']:
        image = Image.open(file_path)
        photo = ImageTk.PhotoImage(image)

        # Crear una nueva ventana para mostrar la imagen
        window = tkinter.Toplevel()
        window.title(file_path)
        label = tkinter.Label(window, image=photo)
        label.image = photo
        label.pack()

    elif file_extension.lower() == '.doc' or file_extension.lower() == '.docx':
        doc = Document(file_path)
        content = [paragraph.text for paragraph in doc.paragraphs]

        # Crear una nueva ventana para mostrar el contenido del archivo
        window = tkinter.Toplevel()
        window.title(file_path)
        text = tkinter.Text(window)
        text.pack()
        for paragraph in content:
            text.insert(tkinter.END, paragraph + '\n')
    else:
        # Tipo de archivo no compatible
        print(f"Tipo de archivo no compatible: {file_extension}")

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
            
#Enviar archivos al server
def send_file(file,file_name):
    client.send("Bytes: {} {}".format(len(file) ,file_name).encode())
    client.send(file)
    size_info = "Archivo enviado: {} ({} bytes)".format(file_name, len(file))
    client.send(size_info.encode())    
    print("Se envio al server el archivo")

#Ventana cliente
screen_cliente = ThemedTk(theme="arc")
screen_cliente.title("Cliente")
username = " "
screen_cliente.configure(bg='#f0f0f0')

# Configuración de estilo para ttk widgets
style = ttk.Style()
style.configure("TButton", foreground="#000", background="#90AFC5", font=("Arial", 12))
style.configure("TEntry", foreground="#000", background="#ffffff", font=("Arial", 12))

#Ventana superior para ingresar nombre de usuario y conectarse al server
frame_user = ttk.Frame(screen_cliente)
label_name = ttk.Label(frame_user, text = "Nombre de usuario:", font=("Arial", 12))
label_name.pack(side=tkinter.LEFT, padx=5, pady=5)
name_user = ttk.Entry(frame_user, width=20)
name_user.pack(side=tkinter.LEFT, padx=5)
button_connect = ttk.Button(frame_user, text="Conectarse", command=lambda : connect())
button_connect.pack(side=tkinter.LEFT, padx=5)
frame_user.pack(side=tkinter.TOP, pady=10)

#Ventana Chat
screen_chat = ttk.Frame(screen_cliente)
label_title = ttk.Label(screen_chat, text="CHAT", font=("Helvetica", 16, "bold"))
label_title.pack(pady=5)
scroll = ttk.Scrollbar(screen_chat)
scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
chat = tkinter.Text(screen_chat, height=35, width=50, font=("Arial", 12), bg='#ECECEC')
chat.pack(pady=5)
chat.tag_config("mensaje", font=("Arial", 12))
scroll.config(command=chat.yview)
chat.config(yscrollcommand=scroll.set, highlightbackground="blue", state="disabled")
screen_chat.pack(side=tkinter.TOP, pady=10)

#Ventana para enviar mensajes y archivos
bottomFrame = tkinter.Frame(screen_cliente, bg='#ECECEC')
msg = tkinter.Text(bottomFrame, height=2, width=30)
msg.pack(side=tkinter.LEFT)
msg.config(highlightbackground="grey", state="disabled")
msg.bind("<Return>", (lambda event: client_send(msg.get("1.0", tkinter.END))))
upload_button = tkinter.Button(bottomFrame, text="Enviar archivo",bg='#ECECEC',command=(lambda: upload_file(bottomFrame)))
upload_button.pack(side=tkinter.LEFT)
button2 = tkinter.Button(text="Ver Archivo",bg='#ECECEC',command=(lambda: view_file(bottomFrame)))
button2.pack(side=tkinter.LEFT)
bottomFrame.pack(side=tkinter.BOTTOM, padx=5)

def cerrar_ventana():
    # Preguntar al usuario si realmente desea cerrar la ventana
    respuesta = tkinter.messagebox.askyesno("Salir", "¿Realmente desea salir?")
    if respuesta == True:
        screen_cliente.destroy()
        os._exit(0)

# Configurar el botón de cierre de la ventana
screen_cliente.protocol("WM_DELETE_WINDOW", cerrar_ventana)

screen_cliente.mainloop()