#! /usr/bin/env python
# encoding: utf-8
"""
Example of a AT command protocol.

https://en.wikipedia.org/wiki/Hayes_command_set
http://www.itu.int/rec/T-REC-V.250-200307-I/en
"""
from __future__ import print_function

import sys
sys.path.insert(0, '..')

import logging
import serial
import serial.threaded
import threading

try:
    import queue
except ImportError:
    import Queue as queue

import time

class ATException(Exception):
    pass


class Uart(serial.threaded.Protocol):

    TERMINATOR = b'\r\n'
    ENCODING = 'utf-8'
    UNICODE_HANDLING = 'replace'

    def __init__(self):
        self.buffer = bytearray()
        self.transport = None

    def connection_made(self, transport):
        """Store transport"""
        self.transport = transport

    def connection_lost(self, exc):
        """Forget transport"""
        self.transport = None
        super(Uart, self).connection_lost(exc)

    def data_received(self, data):
        """Buffer received data, find TERMINATOR, call handle_packet"""
        self.buffer.extend(data)
        while self.TERMINATOR in self.buffer:
            packet, self.buffer = self.buffer.split(self.TERMINATOR, 1)
            #self.handle_packet(packet)
            print(packet)

    def data_write(self, text):
        self.transport.write(text.encode(self.ENCODING, self.UNICODE_HANDLING))

    def handle_packet(self, packet):
        """Process packets - to be overridden by subclassing"""
        raise NotImplementedError('please implement functionality in handle_packet')


ser = serial.serial_for_url('/dev/cu.usbserial', baudrate=230400, timeout=1)
with serial.threaded.ReaderThread(ser, Uart) as uart:
    uart.data_write('1')
    while True:
        time.sleep(1)


