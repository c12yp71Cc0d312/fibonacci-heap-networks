import socket

HEADER = 16
PORT = 5050
FORMAT = 'utf-8'

DISCONNECT_MESSAGE = '!DISCONNECT'
# SERVER = '192.168.0.103'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)    # encode message string into bytes

    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)      # encode message length into bytes
    send_length += b' ' * (HEADER - len(send_length))       # padding message length byte stream to make it HEADER size

    client.send(send_length)
    client.send(message)

    print(client.recv(2048).decode(FORMAT))        # just hardcoding a max message size

send('Hello')
input()             # just so that only after any keypress, the next message is sent
send('World')
input()
send(DISCONNECT_MESSAGE)