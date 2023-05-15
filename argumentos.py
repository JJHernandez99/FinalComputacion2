import argparse
import sys
import socket

def parser():
    # creo la instancia del parser
    parser = argparse.ArgumentParser(description='Trabajo Final Computacion II')
    parser.add_argument('-p', '--port', default=5000, help='Puerto donde se esperan conexiones nuevas', type=int)
    #parser.add_argument('-n', '--name', default="anonimo", help='Nombre de Usuario', type=str)
    parser.add_argument('-i', '--ip', default="127.0.0.1", help='Dirección IP del servidor', type=str)

    args = parser.parse_args()  

    if args.port <= 0 or args.port == 80:
        print("ERROR!!! El numero del puerto no es correcto") 
        sys.exit()


    return args