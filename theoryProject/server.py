import socket
import threading
import randomkeys
import fibonacciHeap
import os

HEADER = 16     # length of header message. since we dont know what would be the message size, the first message
                # the client send would be a HEADER msg of 16 bytes, which tells us the size of the actual message
PORT = 50000

SERVER = socket.gethostbyname(socket.gethostname())     # gets localhost ipv4
ADDR = (SERVER, PORT)

FORMAT = 'utf-8'    # format to decode the bytes message into


# class whose member clientCount contains the no of clients
class ClientCountClass:
    clientCount = 0


# class whose member KEY_PRIORITY contains a dictionary of key:priority values
class KeyPriorities:
    KEY_PRIORITY = {}
    @staticmethod
    def setPriotities():
        for i in range(10000):
            KeyPriorities.KEY_PRIORITY[randomkeys.keys[i]] = i+1


# function to initialize the FibonacciHeap() instance fHeap and the server socket
def initHeapAndSocket():
    fHeap = fibonacciHeap.FibonacciHeap()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)   # binding the server socket to the specified address
    return fHeap, server


# main function
def main():
    KeyPriorities.setPriotities()
    fHeap, serverSocket = initHeapAndSocket()

    print("[STARTING] server is starting...")
    numClients = input('enter no of clients: ')

    start(int(numClients), fHeap, serverSocket)


# function to start receiving on the server socket and handle the incoming client connections
def start(numClients, fHeap, server):

    # make server start listening for connections, and passing them to handle_client to run in a new thread
    server.listen()
    print(f'[LISTENING] Server is listening on {SERVER}')

    connCount, addrCount = server.accept()


    # num of clients msg encoded into bytearray
    sendMsg = str(numClients).encode(FORMAT)

    # encoding len of no of clients msg into bytearray
    msg_length = len(sendMsg)
    send_length = str(msg_length).encode(FORMAT)  # encode message length into bytes
    send_length += b' ' * (HEADER - len(send_length))  # padding message length byte stream to make it HEADER size

    # sending len of the msg and the no of clients msg
    connCount.send(send_length)
    connCount.send(sendMsg)


    clientsLeft = numClients

    print('connection window opened')
    print(f'no of clients left to join: {clientsLeft}')
    # processing each client
    while clientsLeft > 0:
        clientsLeft -= 1

        # server socket accepting a new connection req
        conn, addr = server.accept()    # blocking line
        # waits until a new connection occurs, after which it stores the add of that connection (what ip and port it came from),
        # and we will store an actual socket object conn which will help us send info back to that connection

        # creating a separate thread to handle the current client
        thread = threading.Thread(target=handle_client, args=(conn, addr, fHeap))
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.activeCount() - 1}')    # -1 because 1 thread [start()] is always running

        print(f'no of clients left to join: {clientsLeft}')


    # to wait until all clients establish connection
    while fibonacciHeap.FibonacciHeap.numOfElements != numClients:
        pass

    print('Connection window closed')


    clientsLeft = numClients
    while(clientsLeft > 0):
        # getting the min from the fibonacci heap
        ci = fibonacciHeap.perform_operation(FHEAP=fHeap, OPERATION='min extract')

        # encoding prioirty msg
        sendMsg = f'You have priority {numClients - clientsLeft + 1}'.encode(FORMAT)

        # encoding len of priority msg into bytearray
        msgLen = len(sendMsg)
        sendMsgLen = str(msgLen).encode(FORMAT)
        sendMsgLen += b' ' * (HEADER - len(sendMsgLen))

        # sending len of msg and the priority msg
        ci[0].send(sendMsgLen)
        ci[0].send(sendMsg)

        # opening and reading file to send
        f = open('g.txt', "rb")
        fileSize = os.path.getsize('g.txt')
        l = f.read(fileSize)

        # encoding size of file into bytearray
        fileLength = str(fileSize).encode(FORMAT)
        fileLength += b' ' * (HEADER - len(fileLength))

        # sending size of file and the actual file
        ci[0].send(fileLength)
        ci[0].send(l)

        f.close()
        clientsLeft -= 1


# function to handle each client in a separate thread
def handle_client(conn, addr, fHeap):
    # handle individual connections bw each client and server
    print(f'[NEW CONNECTION] {addr} connected.')

    connection_info = (conn, addr)


    # receiving len of msg
    expectedlength = HEADER
    recvlength = 0
    msg_length = bytearray()
    while expectedlength - recvlength > 0:
        msg_length += conn.recv(expectedlength - recvlength)
        recvlength = len(msg_length)

    msg_length = int(msg_length.decode(FORMAT))


    # receiving the msg (key msg)
    expectedlength = int(msg_length)
    recvlength = 0
    msg = bytearray()
    while expectedlength - recvlength > 0:
        msg += conn.recv(expectedlength - recvlength)
        recvlength = len(msg)

    msg = msg.decode(FORMAT)


    key = msg

    # tuple contains (priority, key) to process in the fibonacciHeap
    pc_tuple = (KeyPriorities.KEY_PRIORITY[key], connection_info)

    # updating no of elements of the heap
    fibonacciHeap.FibonacciHeap.numOfElements += 1

    # inserting the pc_tuple into the heap
    fibonacciHeap.perform_operation(FHEAP=fHeap, OPERATION='insert', PC_TUPLE=pc_tuple)

    print(f'[{addr}] received key: {msg}')

    # encoding conn established msg
    sendMsg = f'received {msg}. Connection established'.encode(FORMAT)

    # encoding size of conn established msg
    msgLen = len(sendMsg)
    sendMsgLen = str(msgLen).encode(FORMAT)
    sendMsgLen += b' ' * (HEADER - len(sendMsgLen))

    # sending the size of msg and the conn established msg
    conn.send(sendMsgLen)
    conn.send(sendMsg)


if __name__ == "__main__":
    main()