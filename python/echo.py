
import socket

HOST = '10.39.249.126'
PORT = 9620

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)

print("wait for connection ...")

while True:
    conn, addr = sock.accept()
    print("Connected by ", addr)

    cmd = conn.recv(128)
    print(cmd);
    conn.send(cmd)
