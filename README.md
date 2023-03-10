# FinalComputacion2
## Repositorio entrega Final Computacion II

## Resumen
La aplicación se basa en un chat multi-cliente con interfaz grafica aplicado en un servidor (TCP como protocolo) basado en hilos donde permite la conexión de múltiples clientes de manera concurrente.
El servidor es el encargado de atender cada uno de clientes que se conectan para poder ingresar a la sala de chat, para elllo es necesario definir la direccion IP y puerto al que se deben conectar los usuarios. Tambien solicita el nombre de cada uno de los usuarios que se unen a la sala de chat. Luego permite transmitir mensajes y compartir archivos entre los cliente conectados

El servidor solicita el nombre de usuario cuando el usuario desea unirse a la sala de chat y acepta la conexión solo si el nombre de usuario es único. Luego transmite el mensaje de un cliente a todos los demás clientes conectados. También informa sobre la entrada/salida de cualquier cliente.

## Elementos Principales
- Uso de Sockets con multiples conexiones de clientes de manera concurrente.
- Mecanismos de IPC 
- Parseo de argumentos por linea de comando
- Entorno Visual (Desktop)
- Despliegue en contenedores Docker

## Diagramas

### Principal

![Diagram-Principal](https://user-images.githubusercontent.com/48955519/222277237-5d543260-c96c-45e7-af59-87ad9468da6d.png)

### Manejo de Sockets

![Diagram-Sockets](https://user-images.githubusercontent.com/48955519/222277392-66e0f48e-f2b0-4550-86ba-3efcc2ceb5a4.png)
