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
        if line.startswith('+'):
            self.events.put(line)
        else:
            self.responses.put(line)

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

        def connection_made(self, transport):
            super(PAN1322, self).connection_made(transport)
            # our adapter enables the module with RTS=low
            self.transport.serial.rts = False
            time.sleep(0.3)
            self.transport.serial.reset_input_buffer()

        def handle_event(self, event):
            """Handle events and command responses starting with '+...'"""
            if event.startswith('+RRBDRES') and self._awaiting_response_for.startswith('AT+JRBD'):
                rev = event[9:9 + 12]
                mac = ':'.join('{:02X}'.format(ord(x)) for x in rev.decode('hex')[::-1])
                self.event_responses.put(mac)
            elif event.startswith('+CGMR') and self._awaiting_response_for.startswith('AT+CGMR'):
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

        # - - - example commands

        def reset(self):
            self.command("AT")      # SW-Reset BT module

        def disable_echo(self):
            self.command("ATE0")

        def get_version(self):
            return self.command_with_event_response("AT+CGMR")

        def get_ccid(self):
            return self.command_with_event_response("AT+CCID")

        def get_cpin(self):
            return self.command_with_event_response("AT+CPIN?")

        def get_signal_quality(self):
            return self.command_with_event_response("AT+CSQ")

        def get_registration(self):
            return self.command_with_event_response("AT+CREG?")

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
