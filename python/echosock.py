#!/usr/bin/env python3

import socket
import select
import time

EOL1 = b'\n'

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(('0.0.0.0', 9900))
serversocket.listen(1)
serversocket.setblocking(0)

print('listen on 0.0.0.0:', 9900)

epoll = select.epoll()
epoll.register(serversocket.fileno(), select.EPOLLIN)

try:
    connections = {}
    request = b''

    while True:
        events = epoll.poll(1)

        for fileno, event in events:

            if fileno == serversocket.fileno():
                conn, address = serversocket.accept()
                print("connect ", conn.fileno(), address)
                conn.setblocking(0)
                epoll.register(conn.fileno(), select.EPOLLIN)
                connections[conn.fileno()] = conn

            elif event & select.EPOLLIN:
                request = connections[fileno].recv(1024)
                if EOL1 in request:
                    print('-> ' + request.decode())
                    s = str(time.time()) + ': ' + request.decode()
                    connections[fileno].send(s.encode('utf-8'))

                if len(request) == 0:
                    print('close connect', fileno)
                    epoll.unregister(fileno)
                    connections[fileno].close()
                    del connections[fileno]

finally:
    epoll.unregister(serversocket.fileno())
    epoll.close()
    serversocket.close()

