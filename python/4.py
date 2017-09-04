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
        """
        Stop the event processing thread, abort pending commands, if any.
        """
        self.alive = False
        self.events.put(None)
        self.responses.put('<exit>')

    def _run_event(self):
        """
        Process events in a separate thread so that input thread is not
        blocked.
        """
        while self.alive:
            try:
                self.handle_event(self.events.get())
            except:
                logging.exception('_run_event')

    def handle_line(self, line):
        """
        Handle input from serial port, check for events.
        """
        print('response: <%r>' % line)
        self.responses.put(line)

    def handle_event(self, event):
        """
        Spontaneous message received.
        """
        print('event received:', event)

    def command(self, command):
        """
        Set an AT command and wait for the response.
        """
        print("command: <%r>" %command)
        with self.lock:  # ensure that just one thread is sending commands at once
            self.transport.write(command.encode(self.ENCODING, self.UNICODE_HANDLING) + b'\r')

    def wait_response(self, r1='OK', r2='ERROR', timeout=1):
        with self.lock:
            while True:
                try:
                    line = self.responses.get(timeout=timeout)
                    if line.startswith(r1):
                            return 1, line
                    elif line == r2:
                        return r2, line

                except queue.Empty:
                    raise ATException('AT command timeout ({%r})' % r1)


# test
if __name__ == '__main__':
    import time

    class PAN1322(ATProtocol):
        """
        Example communication with PAN1322 BT module.

        Some commands do not respond with OK but with a '+...' line. This is
        implemented via command_with_event_response and handle_event, because
        '+...' lines are also used for real events.
        """

        def __init__(self):
            super(PAN1322, self).__init__()

        def connection_made(self, transport):
            super(PAN1322, self).connection_made(transport)
            # our adapter enables the module with RTS=low
            self.transport.serial.rts = False
            time.sleep(0.3)
            self.transport.serial.reset_input_buffer()

        def reset(self):
            self.command('AT')
            return self.wait_response()

        def disable_echo(self):
            self.command('ATE0')
            return self.wait_response()

        def get_version(self):
            self.command("AT+CGMR")
            r, line = self.wait_response('+CGMR')
            if r == 1:
                return r, line[7:]
            else:
                return None, line

        def get_ccid(self):
            self.command("AT+CCID")
            r, line = self.wait_response('+CCID')
            if r == 1:
                return r, line[7:]
            else:
                return None, line

        def get_cpin(self):
            self.command("AT+CPIN?")
            r, line = self.wait_response('+CPIN')
            if r == 1:
                return r, line[7:]
            else:
                return None, line

        def get_signal_quality(self):
            self.command("AT+CSQ")
            r, line = self.wait_response('+CSQ')
            print('get_signal_quality:', line)
            line = line[6:]
            csq = line.split(',', 1)
            return int(csq[0])

        def get_registration(self):
            self.command("AT+CREG?")
            r, line = self.wait_response('+CREG')
            line = line[7:]
            reg = line.split(',', 1)
            return reg[1]

        def get_network_attached(self):
            self.command("AT+CGATT?")
            r, line = self.wait_response('+CGATT')
            attached = line[8:]
            return attached

        def set_apn(self):
            self.command('AT+NETAPN="CMNET","",""')
            return self.wait_response()

        def enable_ppp(self):
            self.command('AT+XIIC=1')
            return self.wait_response()

        def get_ip(self):
            self.command("AT+XIIC?")
            r, line = self.wait_response('+XIIC', timeout=5)
            line = line.split(',', 1)
            ip = line[1]
            return ip

        def tcp_close(self):
            self.command('AT+TCPCLOSE=1')
            return self.wait_response('+TCPCLOSE')

        def tcp_setup(self):
            self.command('AT+TCPSETUP=1,59.110.215.205,9900')
            r, line = self.wait_response('+TCPSETUP', timeout=30)
            line = line[11:].split(',', 1)
            return line[1]

        def tcp_is_connected(self):
            self.command('AT+IPSTATUS=1')
            r, line = self.wait_response('+IPSTATUS')
            line = line.split(',', 3)
            status = line[1]
            return status == 'CONNECT'

        def tcp_send(self, data):
            self.command('AT+TCPSEND=1,' + str(len(data)))

            #self.wait_response('>', timeout=10)
            time.sleep(0.5)
            self.transport.write(data.encode(self.ENCODING, self.UNICODE_HANDLING))

            self.wait_response(timeout=5)
            r, line = self.wait_response('+TCPSEND', timeout=5)
            return r, line

        def tcp_recv(self):
            r, line = self.wait_response('+TCPRECV', timeout=10)
            return r, line


    ser = serial.serial_for_url('/dev/cu.usbserial', baudrate=57600, timeout=1)
    with serial.threaded.ReaderThread(ser, PAN1322) as modem:

        def gsm_init():
            modem.reset()
            modem.disable_echo()
            modem.get_version()

            r, ccid = modem.get_ccid()
            if r is None:
                print('No SIM card found')
                return False

            for i in range(10):
                r, cpin = modem.get_cpin()
                if cpin == 'READY':
                    break
                time.sleep(0.5)
            else:
                return False

            quality = None
            for i in range(10):
                quality = modem.get_signal_quality()
                if quality > 12 and quality != 99:
                    break
                time.sleep(0.5)
            else:
                return False

            for i in range(10):
                reg = modem.get_registration()
                if reg == '1' or reg == '5':
                    break
                time.sleep(1)
            else:
                return False

            for i in range(10):
                attached = modem.get_network_attached()
                if attached == '1':
                    break
                time.sleep(1)
            else:
                return False

        def gsm_enable_gprs():
            modem.set_apn()
            modem.enable_ppp()

            while True:
                ip = modem.get_ip()
                if ip != '0.0.0.0':
                    break
                time.sleep(1)


        def gsm_tcp_connect():
            modem.tcp_close()

            for i in range(3):
                if modem.tcp_setup() == 'OK' and modem.tcp_is_connected():
                    return True
            else:
                return False

        def gsm_tcp_send(data):
                modem.tcp_send(data)

        inited = False
        gprs_enabled = False
        tcp_connected = False

        while True:
            if inited == False:
                inited = gsm_init()
                continue

            if gprs_enabled == False:
                gprs_enabled = gsm_enable_gprs()
                if gprs_enabled == False:
                    inited = False
                continue

            count = 0
            while True:
                count += 1
                print('\r\n'*3, '=================', count)
                if tcp_connected == False:
                    tcp_connected = gsm_tcp_connect()
                    if tcp_connected == False:
                        break

                if modem.tcp_is_connected():
                    gsm_tcp_send(str(time.time()))
                    modem.tcp_recv()
                    time.sleep(90)
                else:
                    tcp_connected = False


