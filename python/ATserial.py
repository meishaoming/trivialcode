#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function

import sys

import logging
import serial
import serial.threaded
import threading

try:
    import queue
except ImportError:
    import Queue as queue

class ATException(Exception):
    pass

class ATProtocol(serial.threaded.LineReader):

    TERMINATOR = b'\r\n'

    def __init__(self):
        super(ATProtocol, self).__init__()
        self.alive = True
        self.responses = queue.Queue()
        self.events = queue.Queue()
        self._event_thread = threading.Thread(target=self._run_event)
        self._event_thread.daemon = True
        self._event_thread.name = 'at-event'
        self._event_thread.start()
        self.lock = threading.Lock()

    def stop(self):
        self.alive = False
        self.events.put(None)
        self.responses.put('<exit>')

    def _run_event(self):
        while self.alive:
            try:
                self.handle_event(self.events.get())
            except:
                logging.exception('_run_event')

    def handle_line(self, line):
        self.responses.put(line)

    def handle_event(selfs, event):
        print('event received:', event)

    def command(self, command, response='OK', timeout=5):
        with self.lock:
            self.write_line(command)
            print("  -> %r" %command)
            lines = []
            while True:
                try:
                    line = self.responses.get(timeout=timeout)
                    print("  <- %r" % (line))
                    if line == response:
                        return lines
                    elif line == 'ERROR':
                        return lines
                    else:
                        lines.append(line)
                except queue.Empty:
                    print("Error: timeout, no output")
                    return

if __name__ == '__main__':

    try:
        ser = serial.serial_for_url('/dev/cu.usbserial', baudrate=115200, timeout=1)
    except serial.SerialException:
        print('serial exception')
    else:
        with serial.threaded.ReaderThread(ser, ATProtocol) as n10:
            while True:
                line = sys.stdin.readline()
                a = line.replace('\n', '\r')
                #a = a.upper()
                n10.command(a, timeout=1)
                print("=========\r\n")
