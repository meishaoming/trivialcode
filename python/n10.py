#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function

import logging
import serial.threaded
import threading

try:
    import queue
except ImportError:
    import Queue as queue

class ATException(Exception):
    pass

class ATProtocol(serial.threaded.Protocol):

    TERMINATOR = b'\r\n'
    ENCODING = 'utf-8'
    UNICODE_HANDLING = 'replace'

    def __init__(self):
        super(ATProtocol, self).__init__()
        self.responses = queue.Queue()
        self.buffer = bytearray()
        self.buffer1 = bytearray()
        self.lock = threading.Lock()
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.transport = None

    def data_received(self, data):
        #print("## %r" % (data))
        self.buffer.extend(data)
        self.buffer1.extend(data)
        while self.TERMINATOR in self.buffer:
            packet, self.buffer = self.buffer.split(self.TERMINATOR, 1)
            self.handle_packet(packet)

    def handle_packet(self, packet):
        self.handle_line(packet.decode(self.ENCODING, self.UNICODE_HANDLING))

    def handle_line(self, line):
        self.responses.put(line)

    def write_line(self, text):
        self.transport.write(text.encode(self.ENCODING, self.UNICODE_HANDLING))

    def command(self, command, response='OK', timeout=1):
        with self.lock:
            self.buffer.clear()
            self.buffer1.clear()
            self.write_line(command)
            lines = []
            retval = False
            while True:
                try:
                    line = self.responses.get(timeout=timeout)
                    timeout = 0.05
                    #print("%r -> %r" % (command, line))
                    lines.append(line)

                    if response in line:
                        retval = True

                except queue.Empty:
                    print("%r -> %r" % (command, self.buffer1.decode(self.ENCODING, self.UNICODE_HANDLING)))
                    return retval

if __name__ == '__main__':

    try:
        ser = serial.serial_for_url('/dev/cu.usbserial', baudrate=57600, timeout=1)
    except serial.SerialException:
        print('serial exception')
    else:
        with serial.threaded.ReaderThread(ser, ATProtocol) as n10:
            # modem init
            n10.command('AT\r')
            n10.command('ATE0\r')
            n10.command('AT+CGMR\r')
            n10.command('AT+CCID\r', response='+CCID:')
            n10.command('AT+CPIN?\r', response='+CPIN:')
            n10.command('AT+CSQ\r', response='+CSQ:')
            n10.command('AT+CREG?\r', response='+CREG:')
            n10.command('AT+CGATT?\r', response='+CGATT:')

            # tcp send
#            n10.command('AT+NETAPN="UNINET","",""\r')
#            n10.command('AT+XIIC=1\r')
#            n10.command('AT+XIIC?\r')
#            n10.command('AT+TCPCLOSE=1\r')

            n10.command('AT+=1\r')

