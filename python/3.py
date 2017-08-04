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
        self.events.put(line)

    def handle_event(self, event):
        """
        Spontaneous message received.
        """
        print('event received:', event)

    def command(self, command, response='OK', timeout=5):
        """
        Set an AT command and wait for the response.
        """
        with self.lock:  # ensure that just one thread is sending commands at once
            self.write_line(command + '\r')
            lines = []
            while True:
                try:
                    line = self.responses.get(timeout=timeout)
                    print("%s -> %r" % (command, line))
                    if line == response:
                        return lines
                    else:
                        lines.append(line)
                except queue.Empty:
                    raise ATException('AT command timeout ({!r})'.format(command))

    def command_wait_response(self, command, r1=None, r2=None, r3=None, timeout=1):
        with self.lock:
            self.transport.write(b'%b\r' % (command.encode(self.ENCODING, self.UNICODE_HANDLING)))
            while True:
                try:
                    line = self.responses.get(timeout=timeout)

                    if r1 is not None and line == r1:
                        return 1, line
                    elif r2 is not None and line == r2:
                        return 2, line
                    elif r3 is not None  and line == r3:
                        return 3, line

                except queue.Empty:
                    raise ATException('AT command timeout ({!r})'.format(command))


def parse_ok_error(line):
    if line == 'OK': return 'ok'
    elif line == 'ERROR': return 'fail'
    else: return 'unkonwn'


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
            self.event_responses = queue.Queue()
            self._awaiting_response_for = None
            self._response_parser = None

        def connection_made(self, transport):
            super(PAN1322, self).connection_made(transport)
            # our adapter enables the module with RTS=low
            self.transport.serial.rts = False
            time.sleep(0.3)
            self.transport.serial.reset_input_buffer()

        def handle_event(self, event):
            """Handle events and command responses starting with '+...'"""
            retval = self._response_parser(event)
            if retval == 'ok' or retval == 'fail':
                self.event_responses.put(mac)

            if event.startswith('+CGMR') and self._awaiting_response_for.startswith('AT+CGMR'):
                rev = event[7:]
                self.event_responses.put(rev)
            elif event.startswith('+CCID') and self._awaiting_response_for.startswith('AT+CCID'):
                rev = event[7:]
                self.event_responses.put(rev)
            elif event.startswith('+CPIN') and self._awaiting_response_for.startswith('AT+CPIN?'):
                rev = event[7:]
                self.event_responses.put(rev)
            elif event.startswith('+CSQ') and self._awaiting_response_for.startswith('AT+CSQ'):
                rev = event[6:]
                csq = rev.split(',', 1)
                self.event_responses.put(csq[0])
            elif event.startswith('+CREG') and self._awaiting_response_for.startswith('AT+CREG?'):
                rev = event[7:]
                reg = rev.split(',', 1)
                self.event_responses.put(reg[1])

            elif event.startswith('+CGATT') and self._awaiting_response_for.startswith('AT+CGATT?'):
                rev = event[8:]
                self.event_responses.put(rev)

            elif event.startswith('+XIIC') and self._awaiting_response_for.startswith('AT+XIIC?'):
                rev = event[7:]
                ip = rev.split(',', 1)[1]
                self.event_responses.put(ip)

            elif event.startswith('+TCPCLOSE') and self._awaiting_response_for.startswith('AT+TCPCLOSE'):
                ok = event[11:]
                self.event_responses.put(ok)

            elif event.startswith('+TCPSETUP') and self._awaiting_response_for.startswith('AT+TCPSETUP'):
                ok = event.split(',', 1)[1]
                self.event_responses.put(ok)

            elif event.startswith('+TCPACK') and self._awaiting_response_for.startswith('AT+TCPACK'):
                ok = event.split(',', 1)[1]
                self.event_responses.put(ok)

            else:
                logging.warning('unhandled event: {!r}'.format(event))

        def command_with_event_response(self, command, timeout=1):
            """Send a command that responds with '+...' line"""
            with self.lock:  # ensure that just one thread is sending commands at once
                self._awaiting_response_for = command
                self.transport.write(b'%b\r' % (command.encode(self.ENCODING, self.UNICODE_HANDLING)))
                response = self.event_responses.get(timeout=timeout)
                self._awaiting_response_for = None
                return response

        def commandAT(self, command, parser, timeout=1):
            """Send a command that responds with '+...' line"""
            with self.lock:  # ensure that just one thread is sending commands at once
                self._awaiting_response_for = command
                self._response_parser = parser
                self.transport.write(b'%b\r' % (command.encode(self.ENCODING, self.UNICODE_HANDLING)))
                response = self.event_responses.get(timeout=timeout)
                self._awaiting_response_for = None
                return response

        # - - - example commands

        def reset(self):
            r, line = self.command_wait_response("AT", r1='OK')      # SW-Reset BT module
            return r == 1, line

        def disable_echo(self):
            r, line = self.command_wait_response("ATE0", r1='OK')
            return r == 1, line

        def get_version(self):
            r, line = self.command_wait_response("AT+CGMR", r1='+CGMR')
            if r == 1:
                return True, line[7:]
            else:

        def get_ccid(self):
            r, line = self.command_wait_response("AT+CCID", r1='+CCID')
            if r == 1:
                return True, line[7:]
            else:
                return False, line

        def get_cpin(self):
            r, line = self.command_wait_response("AT+CPIN?", r1='+CPIN')
            if r == 1:
                return True, line[7:]
            else:
                return False, line

        def get_signal_quality(self):
            r, line = self.command_wait_response("AT+CSQ", r1='+CSQ')
            if r == 1:
                csq = line[6:].split(',', 1)
                return True, int(csq[0])
            else:
                return False, line

        def get_registration(self):
            r, line = self.command_wait_response("AT+CREG?")

        def get_network_attached(self):
            return self.command_with_event_response("AT+CGATT?")

        def set_apn(self):
            return self.command('AT+NETAPN="CMNET","",""')

        def enable_ppp(self):
            return self.command('AT+XIIC=1')

        def get_ppp(self):
            return self.command_with_event_response("AT+XIIC?", timeout=5)

        def tcp_close(self):
            return self.command_with_event_response('AT+TCPCLOSE=1')

        def tcp_setup(self):
            return self.command_with_event_response('AT+TCPSETUP=1,59.110.215.205,9900', timeout=30)

        def tcp_check(self):
            return self.command_with_event_response('AT+TCPACK=1')

        def tcp_send(self, data):
            length = len(data)
            return self.command_with_event_response('AT+TCPACK=1,'+len)



    ser = serial.serial_for_url('/dev/cu.usbserial', baudrate=57600, timeout=1)
    #~ ser = serial.Serial('COM1', baudrate=115200, timeout=1)
    with serial.threaded.ReaderThread(ser, PAN1322) as bt_module:

        '''
        '''
        bt_module.reset()
        bt_module.disable_echo()
        print("reset OK")
        print(bt_module.get_version())
        print(bt_module.get_ccid())

        while True:
            cpin = bt_module.get_cpin()
            print('CPIN?', cpin)
            if cpin == 'READY':
                break
            time.sleep(1)

        for i in range(10):
            quality = int(bt_module.get_signal_quality())
            print('signal quality', quality)
            if quality > 12 and quality != 99:
                break
            time.sleep(1)

        for i in range(10):
            registration = bt_module.get_registration()
            print('CREG', registration)
            if registration == '1' or registration == '5':
                break
            time.sleep(1)

        for i in range(20):
            attach = bt_module.get_network_attached()
            print('Attached', attach)
            if attach == '1':
                break
            time.sleep(1)

        print(bt_module.set_apn())
        print(bt_module.enable_ppp())

        time.sleep(1)

        for i in range(20):
            ip = bt_module.get_ppp()
            print('ip', ip)
            if ip != '0.0.0.0':
                break;
            time.sleep(1)


        print(bt_module.tcp_close())

        for i in range(3):
            setup = bt_module.tcp_setup()
            print(setup)
            if setup == 'OK':
                break
            time.sleep(1)

        for i in range(10):
            print(bt_module.tcp_check())
            time.sleep(1)






        #print("MAC address is", bt_module.get_mac_address())
