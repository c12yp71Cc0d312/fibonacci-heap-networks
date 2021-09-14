import socket
import threading
import time
import fibonacciHeap

HEADER = 16     # length of header message. since we dont know what would be the message size, the first message
                # the client send would be a HEADER of 16 bytes, which tells us the size of the actual message
PORT = 5050

# SERVER = '192.168.0.103'    #ipv4 ofthis device
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

FORMAT = 'utf-8'    # format to decode the bytes message into

DISCONNECT_MESSAGE = '!DISCONNECT'  # if this message is received, we will close the connection and disconnect client from the server

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# family - AF_INET (type of address, here, ipv4)
# type - SOCK_STREAM (sends data as stream)

server.bind(ADDR)   # binding the server socket to the specified address

def handle_client(conn, addr):
    # handle individual connections bw each client and server
    print(f'[NEW CONNECTION] {addr} connected.')

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)       # blocking line - wont pass until we receive a message
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f'[{addr}] {msg}')
            conn.send('Message receied'.encode(FORMAT))

    conn.close()


def start():
    # make server start listening for connections, and passing them to handle_client to run in a new thread
    server.listen()
    print(f'[LISTENING] Server is listening on {SERVER}')

    time_limit = 30     # duration for which connections will be accepted
    start_time = time.time()
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time

        if elapsed_time <= time_limit:
            conn, addr = server.accept()    # blocking line
            # waits until a new connection occurs, after which it stores the add of that connection (what ip and port it came from),
            # and we will store an actual socket object conn which will help us send info back to that connection
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f'[ACTIVE CONNECTIONS] {threading.activeCount() - 1}')    # -1 because 1 thread [start()] is always running

        else:
            break



print("[STARTING] server is starting...")
start()