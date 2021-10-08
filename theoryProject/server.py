import socket
import threading
import randomkeys
import fibonacciHeap
import os

HEADER = 16     # length of header message. since we dont know what would be the message size, the first message
                # the client send would be a HEADER of 16 bytes, which tells us the size of the actual message
PORT = 5050

# SERVER = '192.168.0.103'    #ipv4 ofthis device
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

FORMAT = 'utf-8'    # format to decode the bytes message into

# DISCONNECT_MESSAGE = '!DISCONNECT'  # if this message is received, we will close the connection and disconnect client from the server
nc = 0

class ClientCountClass:
    clientCount = 0


class KeyPriorities:
    KEY_PRIORITY = {}
    @staticmethod
    def setPriotities():
        for i in range(10000):
            KeyPriorities.KEY_PRIORITY[randomkeys.keys[i]] = i+1


def initHeapAndSocket():
    fHeap = fibonacciHeap.FibonacciHeap()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)   # binding the server socket to the specified address
    return fHeap, server


def main():
    KeyPriorities.setPriotities()
    fHeap, serverSocket = initHeapAndSocket()

    print("[STARTING] server is starting...")
    numClients = input('enter no of clients: ')

    start(int(numClients), fHeap, serverSocket)


def start(numClients, fHeap, server):
    # make server start listening for connections, and passing them to handle_client to run in a new thread
    server.listen()
    print(f'[LISTENING] Server is listening on {SERVER}')

    connCount, addrCount = server.accept()
    # connCount.send(str(numClients).encode(FORMAT))

    sendMsg = str(numClients).encode(FORMAT)
    msg_length = len(sendMsg)
    send_length = str(msg_length).encode(FORMAT)  # encode message length into bytes
    send_length += b' ' * (HEADER - len(send_length))  # padding message length byte stream to make it HEADER size

    connCount.send(send_length)
    connCount.send(sendMsg)

    clientsLeft = numClients

    print('connection window opened')
    print(f'no of clients left to join: {clientsLeft}')
    while clientsLeft > 0:
        clientsLeft -= 1

        conn, addr = server.accept()    # blocking line
        # waits until a new connection occurs, after which it stores the add of that connection (what ip and port it came from),
        # and we will store an actual socket object conn which will help us send info back to that connection
        thread = threading.Thread(target=handle_client, args=(conn, addr, fHeap))
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.activeCount() - 1}')    # -1 because 1 thread [start()] is always running

        print(f'no of clients left to join: {clientsLeft}')

    while fibonacciHeap.FibonacciHeap.numOfElements != numClients:
        print(f'no of elements in heap is {fibonacciHeap.FibonacciHeap.numOfElements}')

    print('Connection window closed')

    clientsLeft = numClients
    while(clientsLeft > 0):
        ci = fibonacciHeap.perform_operation(FHEAP=fHeap, OPERATION='min extract')
        sendMsg = f'You have priority {numClients - clientsLeft + 1}'.encode(FORMAT)
        msgLen = len(sendMsg)
        sendMsgLen = str(msgLen).encode(FORMAT)
        sendMsgLen += b' ' * (HEADER - len(send_length))

        ci[0].send(sendMsgLen)
        ci[0].send(sendMsg)
        # ci[0].send(f'You have priority {numClients - clientsLeft + 1}'.encode(FORMAT))

        f = open('filename.ext', "rb")
        fileSize = os.path.getsize('filename.ext')
        l = f.read(fileSize)
        fileLength = str(fileSize).encode(FORMAT)
        fileLength += b' ' * (HEADER - len(fileLength))
        ci[0].send(fileLength)
        ci[0].send(l)

        f.close()
        clientsLeft -= 1
        # ci[0].close()


def handle_client(conn, addr, fHeap):
    # handle individual connections bw each client and server
    print(f'[NEW CONNECTION] {addr} connected.')

    connection_info = (conn, addr)

    # connected = True
    # while connected:
    msg_length = conn.recv(HEADER).decode(FORMAT)       # blocking line - wont pass until we receive a message
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)

        key = msg
        pc_tuple = (KeyPriorities.KEY_PRIORITY[key], connection_info)
        fibonacciHeap.FibonacciHeap.numOfElements += 1
        fibonacciHeap.perform_operation(FHEAP=fHeap, OPERATION='insert', PC_TUPLE=pc_tuple)

        print(f'[{addr}] {msg}')
        sendMsg = f'received {msg}. Connection established'.encode(FORMAT)
        msgLen = len(sendMsg)
        sendMsgLen = str(msgLen).encode(FORMAT)
        sendMsgLen += b' ' * (HEADER - len(sendMsgLen))

        conn.send(sendMsgLen)
        conn.send(sendMsg)
        # conn.send(f'received {msg}. Connection established'.encode(FORMAT))


if __name__ == "__main__":
    main()
