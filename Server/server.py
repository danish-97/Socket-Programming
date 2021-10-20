"""
Server side for the Socket Programming COSC264 Asssignment.
The server side listens to incoming connections from the client and then
performs an infinte loop which then sends the data of the file to it.
Author: 'Danish Jahangir'  '28134926'
"""

import socket
import sys
import os

def server():
    """Function that checks if the entered port number is within the given parameters
    and starts running the program if it is"""
    port_num = int(input("Enter a port number(between 1024 and 64000):\n"))
    if port_num > 64000 or port_num < 1024:
        print("Port number entered is invalid")
        sys.exit()
    else:
        create_socket(port_num)
        
def create_socket(port):
    """Function which creates the socket"""
    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        new_socket.bind(('', port))
    except:
        print("Error: Socket binding was unsuccesful")
        new_socket.close()
        sys.exit()
    listen(new_socket)
    
def listen(new_socket):
    """Function that implements the call listen() on the socket"""
    try:
        new_socket.listen()
    except:
        print("Error: Connection unsuccessful")
        new_socket.close()
        sys.exit()
    loop(new_socket)

def loop(new_socket):
    """Function that performs the infinite loop of accepting new connections
    and reading file requests"""
    while True:
        print("\nAwaiting Incoming Connection")
        conn, addr = new_socket.accept()
        print(f"Connection from {addr}")
        file_request(conn)

def file_request(conn):
    """Function that reads a file request record from the connection"""
    try:
        file = conn.recv(1029)
    except:
        print("Error: File request failed")
        conn.close()
        sys.exit()
    process(file, conn)

def process(file, conn):
    """Function that verifies the validity of the file request record"""
    request = bytearray(file)
    if len(request) < 5:
        print("Error: Insufficient number of bytes")
        conn.close()
    elif (((request[0] << 8 )| request[1] & 0xFF) != 0x497E):
        print("Error: Magic Number Mismatch")
        conn.close()
    elif (int(request[2]) != 1):
        print("Error: Version Mismatch")
        conn.close()
    elif (int(((request[3] << 8 )| (request[4] & 0xFF))) < 1
         or int(((request[3] << 8 )| (request[4] & 0xFF))) > 1024):
         print("Error: Invalid Length")
         conn.close()
    else:
        open_file(request, conn)

def open_file(request, conn):
    """Function that opens the file and reads the data in it"""
    file = request[5:]
    filename = file.decode('utf-8').strip()
    print("filename", filename)
    data = None
    is_open = True
    try:
        new_file = open(filename, 'rb')
        data = new_file.read()
        print("hello", data)
        new_file.close()
        print("Opened File- Wrote Data")
    except Exception as e:
        print(e)
        is_open = False
    send(data, conn, is_open)

def send(data, conn, is_open):
    """Function that sends the data of the file to the client"""
    packet = build(data, is_open)
    conn.send(packet)
    conn.close()
    print(f"Transferred {packet} bytes to client")

def build(data, is_open):
    """Function that returns the built packet"""
    is_build = 0
    if is_open == True:
        is_build = 1

    res = bytearray([(0x497E) >> 8, (0x497E & 0xFF), 0x2, is_build])

    if is_open:
        res.append((len(data) >> 24))
        res.append((len(data) >> 16 & 0xFF))
        res.append((len(data) >> 8 & 0xFF))
        res.append((len(data) & 0xFF))
        for i in data:
            res.append(i)
    return res

server()
        
