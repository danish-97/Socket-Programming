"""
Client side for the Socket Programming COSC264 Asssignment.
The client side attempts to connect to the server and recieves the required
data from it.
Author: 'Danish Jahangir'  '28134926'
"""

import socket
import sys
import os
import math
    
def address(ip_address):
    """Function that returns the ip address of the server input by a user"""
    try:
        res = socket.gethostbyname_ex(ip_address)
        print(res)
        return res[2][0]
    except:
        print("Error: Entered IP address is invalid.")
        sys.exit()
        
def port_number():
    """Function that verifies the given conditions for the port number and 
    returns the number if satisfied"""
    port_num = int(input("Enter a port number(between 1024 and 64000):\n"))
    if port_num > 64000 or port_num < 1024:
        print("Port number entered is invalid")
        sys.exit()
    else:
        return port_num
    
def file_name():
    """Function that retirves the name of the file the client wants from the 
    server and prints an error message if file already exists"""
    file = input("Name of file to be retrived:\n")
    if file in os.listdir():
        print("Error: File already exists")
        sys.exit()
    else:
        return file

def create_socket():
    """Function that creates the socket for the client"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return client_socket
    except:
        print("Error: Socket Creation was unsuccessful")
        sys.exit()

def connect(client_socket, server_address, port):
    """Function that connects the client to the server"""
    try:
        client_socket.connect((server_address, port))
    except:
        print("Error: Client connection to server failed")
        sys.exit()

def send_file(client_socket, file):
    """Function that sends the file request to the server"""
    magic_num = 0x497E
    request = bytearray()
    request.append((magic_num) >> 8)
    request.append((magic_num & 0xFF))
    request.append(0x01)
    request.append(len(file.encode()) >> 8)
    request.append((len(file.encode()) & 0xFF))
    for i in file.encode():
        request.append(i)
    client_socket.send(request)

def read_file(client_socket, file):
    """Function that checks the validity of the header of the 
    file response sent by the server"""
    try:
        data = client_socket.recv(8)
    except:
        print("Error: File response unsuccessful")
        client_socket.close()
    array = bytearray(data)
    if array[2] != 2:
        print("Error: Invalid type of file")
        client_socket.close()
    elif array[3] == 0:
        print("Error: File does not exist")
        client_socket.close()
    elif (((array[0] << 8) | array[1]) != 0x497E):
        client_socket.close()
        print("Error: Invalid Magic Number")
    else:
        read(array[4:], client_socket, file)

def read(byte_length, client_socket, file):
    """Function that reads the file"""
    length = int(byte_length[0] << 24 | byte_length[1] << 16 |
        byte_length[2] << 8 | byte_length[3])
    file_1 = open(file, "wb")
    total = 0
    for i in range(0, math.floor(length / 4096)):
        total += 4096
        try:
            current = bytearray(client_socket.recv(4096))
        except:
            print("Error: File data was corrupted")
            client_socket.close()
            sys.exit()
        file_1.write(current)
    total += length % 4096
    try:
        last = bytearray(client_socket.recv(length % 4096))
    except:
        print("Error: File data was corrupted")
        client_socket.close()
        sys.exit()
    file_1.write(last)
    print(f"Transfer Complete: {total} bytes recieved from server")
    file_1.close()

def client():
    """The main function of the program that runs the client"""
    #User inputs the required information
    ip_address = input("Enter the IP address for the server:\n")
    server_address = address(ip_address)
    port = port_number()
    filename = file_name()

    #Creates the socket
    client_socket = create_socket()

    #Attempts to connect to the server
    connect(client_socket, server_address, port)

    #Sends the required file request to the server
    send_file(client_socket, filename)

    #Reads the file recieved
    read_file(client_socket, filename)

client()