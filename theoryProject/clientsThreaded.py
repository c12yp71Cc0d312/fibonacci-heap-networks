import random
import socket
import threading
import randomkeys
import time
import os
import shutil

HEADER = 16
PORT = 5050
FORMAT = 'utf-8'
start_time = time.perf_counter()

# SERVER = '192.168.0.103'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

clientSockets = []
socketClientCount = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketClientCount.connect(ADDR)

numOfClients = 0


if os.path.isdir('received'):
    shutil.rmtree('received')
os.mkdir('received')


def getCount():
    global numOfClients
    msg = socketClientCount.recv(2048)
    msg = msg.decode(FORMAT)
    print(f'clientCount received: {msg}')
    numOfClients = int(msg)


def initClientSockets():
    for i in range(numOfClients):
        clientSockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        clientSockets[i].connect(ADDR)


def main():
    getCount()
    initClientSockets()

    keysList = randomkeys.keys
    print(f'no of clients: {numOfClients}')
    random.shuffle(keysList)
    for i in range(numOfClients):
        key = keysList[i]
        thread = threading.Thread(target=sendAndReceiveData, args=(key, clientSockets[i], i))
        thread.start()


count = 1
def sendAndReceiveData(key, client, clientNum):
    global count
    print(f'client {clientNum} sending key {key}')
    send(key, client, clientNum)

    while True:
        msg = client.recv(2048)

        try:
            msg = msg.decode(FORMAT)
            print(f'client {clientNum} received: {msg}')
            # if(count == numOfClients):
            #     end_time = time.perf_counter()
            #     print("\n\n", end_time - start_time, "seconds")
            count += 1
            break
        except:
            pass

    filesize = int(client.recv(HEADER).decode(FORMAT))
    print(f'client {clientNum} received: file size is {filesize}')
    print(f'client {clientNum} starting to receive file')
    recFile = client.recv(filesize)
    with open(f'received/file{clientNum}.ext', 'wb') as f:
        f.write(recFile)
    print(f'client {clientNum} has received the file')
    client.close()


def send(msg, client, clientNum):
    message = msg.encode(FORMAT)    # encode message string into bytes

    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)      # encode message length into bytes
    send_length += b' ' * (HEADER - len(send_length))       # padding message length byte stream to make it HEADER size

    client.send(send_length)
    client.send(message)

    msg = client.recv(2048).decode(FORMAT)        # just hardcoding a max message size
    print(f'client {clientNum} received msg from server: {msg}')


if __name__ == "__main__":
    main()