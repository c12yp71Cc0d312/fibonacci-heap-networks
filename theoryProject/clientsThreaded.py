import random
import socket
import threading
import randomkeys
HEADER = 16
PORT = 5050
FORMAT = 'utf-8'

DISCONNECT_MESSAGE = '!DISCONNECT'
# SERVER = '192.168.0.103'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

clientSockets = []

numOfClients = 10000

for i in range(numOfClients):
    clientSockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    clientSockets[i].connect(ADDR)


def send(msg, client, clientNum):
    message = msg.encode(FORMAT)    # encode message string into bytes

    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)      # encode message length into bytes
    send_length += b' ' * (HEADER - len(send_length))       # padding message length byte stream to make it HEADER size

    client.send(send_length)
    client.send(message)

    msg = client.recv(2048).decode(FORMAT)        # just hardcoding a max message size
    print(f'client {clientNum} received msg from server: {msg}')


def sendAndReceiveData(key, client, clientNum):
    print(f'client {clientNum} sending key {key}')
    send(key, client, clientNum)
    # send('P6VG2yrfKE')
    # input()             # just so that only after any keypress, the next message is sent
    # send('World')
    # input()
    # send(DISCONNECT_MESSAGE)

    while True:
        msg = client.recv(2048)

        try:
            msg = msg.decode(FORMAT)
            print(f'client {clientNum} received: {msg}')
        except:
            pass
            # try:
            #     dataObj = pickle.loads(msg)
            #     print(f'received: int {dataObj.intVal}, float {dataObj.floatVal}, char {dataObj.charVal}')
            #     send(DISCONNECT_MESSAGE)
            #     break
            # except:
            #     pass


keysList = randomkeys.keys



random.shuffle( keysList )
for i in range(numOfClients):
    key = keysList[i]
    thread = threading.Thread(target=sendAndReceiveData, args=(key, clientSockets[i], i))
    thread.start()
    # sendAndReceiveData(key, clientSockets[i])