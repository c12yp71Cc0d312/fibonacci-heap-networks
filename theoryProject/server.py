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

KEY_PRIORITY = {'NVlmeNRzf7': 1,
                'xLrzS5gq0j': 2,
                'QuQtu3NUus': 3,
                'SO7NZPfjDv': 4,
                'Cg19Dptlbt': 5,
                'P6VG2yrfKE': 6,
                'f4vqNin2fB': 7,
                'KVordqgoIJ': 8,
                '4Osgxwn47b': 9,
                'ksfAh4fdfd': 10
}

fHeap = fibonacciHeap.FibonacciHeap()

# connection_info = (conn, addr)
# pc_tuple = (KEY_PRIORITY[key], connection_info)
# fibonacciHeap.perform_operation(FHEAP=fHeap, OPERATION='insert', PC_TUPLE=pc_tuple)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# family - AF_INET (type of address, here, ipv4)
# type - SOCK_STREAM (sends data as stream)

server.bind(ADDR)   # binding the server socket to the specified address

def handle_client(conn, addr):
    # handle individual connections bw each client and server
    print(f'[NEW CONNECTION] {addr} connected.')

    connection_info = (conn, addr)

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)       # blocking line - wont pass until we receive a message
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            else:
                key = msg
                pc_tuple = (KEY_PRIORITY[key], connection_info)
                fibonacciHeap.perform_operation(FHEAP=fHeap, OPERATION='insert', PC_TUPLE=pc_tuple)

            print(f'[{addr}] {msg}')
            conn.send(f'received {msg}'.encode(FORMAT))

    # conn.close()


def start(numClients):
    # make server start listening for connections, and passing them to handle_client to run in a new thread
    # server.settimeout(30)
    server.listen()
    print(f'[LISTENING] Server is listening on {SERVER}')

    # try:
    # time_limit = 30     # duration for which connections will be accepted
    # start_time = time.time()

    clientsLeft = numClients

    print('connection window opened')
    print(f'no of clients left to join: {clientsLeft}')
    while clientsLeft > 0:
        clientsLeft -= 1
    # while time.time() <= start_time + time_limit:
        # current_time = time.time()
        # elapsed_time = current_time - start_time
        # print(f'elapsed: {elapsed_time}')

        # if elapsed_time <= time_limit:
        conn, addr = server.accept()    # blocking line
        # waits until a new connection occurs, after which it stores the add of that connection (what ip and port it came from),
        # and we will store an actual socket object conn which will help us send info back to that connection
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.activeCount() - 1}')    # -1 because 1 thread [start()] is always running

        print(f'no of clients left to join: {clientsLeft}')
        # else:
        #
        #     break

    # except:
    # time.sleep(2)
    print('Connection window closed')

    clientsLeft = numClients
    while(clientsLeft > 0):
        ci = fibonacciHeap.perform_operation(FHEAP=fHeap, OPERATION='min extract')
        ci[0].send('data sent from server'.encode(FORMAT))
        clientsLeft -= 1


print("[STARTING] server is starting...")
numClients = input('enter no of clients: ')
start(int(numClients))
