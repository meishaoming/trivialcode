#!/usr/bin/env python3

import socket
import sys

def echo(host="0", port=9900):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind((host, port))
    sock.listen(10)
    print("wait for connection ...")

    while True:
        conn, addr = sock.accept()
        print("Connected by ", addr)

        while True:
            cmd = conn.recv(128)
            if len(cmd) == 0:
                conn.close()
                break;

            print(cmd);
            conn.send(cmd)

if __name__ == '__main__':
    echo()
