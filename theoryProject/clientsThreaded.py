import random
import socket
import threading
import randomkeys
import time
import os
import shutil

HEADER = 16
PORT = 50000
FORMAT = 'utf-8'
start_time = time.perf_counter()

SERVER = socket.gethostbyname(socket.gethostname())         # gets localhost ipv4
ADDR = (SERVER, PORT)

# a list of sockets for each client
clientSockets = []

# socket to receive the no of clients from the server
socketClientCount = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketClientCount.connect(ADDR)


numOfClients = 0
avg_latency = 0.0


# creating received dir if it doesnt exist, else deleting current one and creating new one
if os.path.isdir('received'):
    shutil.rmtree('received')
os.mkdir('received')


# function to get no of clients value from the server
def getCount():
    global numOfClients

    recLen = int(socketClientCount.recv(HEADER).decode(FORMAT))
    msg = socketClientCount.recv(recLen)
    msg = msg.decode(FORMAT)
    print(f'clientCount received: {msg}')
    numOfClients = int(msg)


# function to initialize the sockets for each client
def initClientSockets():
    for i in range(numOfClients):
        clientSockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        clientSockets[i].connect(ADDR)


# main function
def main():
    getCount()
    initClientSockets()

    keysList = randomkeys.keys
    print(f'no of clients: {numOfClients}')
    random.shuffle(keysList)

    # creating a separate thread to process each client socket
    for i in range(numOfClients):
        key = keysList[i]
        thread = threading.Thread(target=sendAndReceiveData, args=(key, clientSockets[i], i))
        thread.start()

def convert_bytes(size):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0

    return size


count = 1   # to keep track of no of files received
sumFileSizes = 0    # sum of sizes all files received files

# function calls send(), and receives the priority msg and the file sent by the server
def sendAndReceiveData(key, client, clientNum):
    global count
    global avg_latency
    global sumFileSizes
    print(f'client {clientNum} sending key {key}')

    # passes the key value to send()
    send(key, client, clientNum)


    # priority msg size
    expectedlength = HEADER
    recvlength = 0
    recLen = bytearray()
    while expectedlength - recvlength > 0:
        recLen += client.recv(expectedlength - recvlength)
        recvlength = len(recLen)

    recLen = int(recLen.decode(FORMAT))


    # prioirty msg
    expectedlength = int(recLen)
    recvlength = 0
    recMsg = bytearray()
    while expectedlength - recvlength > 0:
        recMsg += client.recv(expectedlength - recvlength)
        recvlength = len(recMsg)

    recMsg = recMsg.decode(FORMAT)
    print(f'client {clientNum} received (priority): {recMsg}---')


    # rec file size
    expectedlength = HEADER
    recvlength = 0
    filesize = bytearray()
    while expectedlength - recvlength > 0:
        filesize += client.recv(expectedlength - recvlength)
        recvlength = len(filesize)

    filesize = int(filesize.decode(FORMAT))

    print(f'client {clientNum} received: file size is {filesize}')
    print(f'client {clientNum} starting to receive file')


    # adding current file size to total file sizes sum
    sumFileSizes += filesize


    # rec file
    expectedlength = int(filesize)
    recvlength = 0
    totFileLenRec = 0
    recFile = bytearray()
    latency_start = time.perf_counter()
    while expectedlength - recvlength > 0:
        recFile += client.recv(expectedlength - recvlength)
        recvlength = len(recFile)
        totFileLenRec += recvlength
    latency_end = time.perf_counter()

    avg_latency += latency_end - latency_start
    print(f'Client {clientNum} latencytime: {latency_end - latency_start} seconds---')

    # writing received file
    with open(f'received/file{clientNum}.txt', 'wb') as f:
        f.write(recFile)
    print(f'client {clientNum} has received the file')


    # checking whether all clients processed in order to stop timer
    if (count == numOfClients):
        end_time = time.perf_counter()
        print(f'\nTotal time taken: {end_time - start_time} seconds')
        avg_latency = avg_latency/numOfClients
        avg_file_size = convert_bytes(sumFileSizes/numOfClients)
        print(f'\nAverage Latency for average file size of {avg_file_size} is: {avg_latency}')
    count += 1
    client.close()


# sends the key to the server and receives an acknowledgement msg of conn established
def send(msg, client, clientNum):
    # encoding the msg containing the key into a bytearray
    message = msg.encode(FORMAT)    # encode message string into bytes

    # encoding len of key msg into a bytearray
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)      # encode message length into bytes
    send_length += b' ' * (HEADER - len(send_length))       # padding message length byte stream to make it HEADER size

    # sending key msg length and the key msg
    client.send(send_length)
    client.send(message)


    # conn establish msg size
    expectedlength = int(HEADER)
    recvlength = 0
    recLen = bytearray()
    while expectedlength - recvlength > 0:
        recLen += client.recv(expectedlength - recvlength)
        recvlength = len(recLen)

    recLen = int(recLen.decode(FORMAT))


    # conn establish msg
    expectedlength = int(recLen)
    recvlength = 0
    recMsg = bytearray()
    while expectedlength - recvlength > 0:
        recMsg += client.recv(expectedlength - recvlength)
        recvlength = len(recMsg)

    recMsg = recMsg.decode(FORMAT)
    print(f'client {clientNum} received msg from server (establish): {recMsg}---')



if __name__ == "__main__":
    main()