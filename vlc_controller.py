#!/usr/bin/env python

import time
import socket
import subprocess

BUFF_SIZE = 1024
SOCK_NAME = 'vlc_socket'
VLC_ARGS = [
    '/usr/bin/cvlc',
    '-I',
    'oldrc',
    '--rc-unix',
    SOCK_NAME,
    '--no-rc-show-pos',
    '--quiet',
    '-f',
    '--no-osd'
]


class VLCController:

    def __init__(self):
        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.settimeout(3)

        subprocess.Popen(VLC_ARGS)
        time.sleep(3)  # Waiting for VLC to start
        self.sock.connect(SOCK_NAME)

    def _parse_response(self):
        """
        Reads data from socket, filtering status update"""
        raw_recv = self.sock.recv(BUFF_SIZE)
        lines = [line.strip() for line in raw_recv.split(b'\n')]
        res = []

        for line in lines:
            if not line:
                continue
            if line.startswith(b'Trying to add'):
                continue
            if line.startswith(b'status change:'):
                continue
            res.append(line)
        return res

    def _send_command(self, query):
        """
        Sends a command through the socket and return the recieved lines"""
        self.sock.send(query)
        resp = None
        while not resp:
            resp = self._parse_response()
        return resp

    def get_progress(self):
        """
        Returns a the elapsed time and the stream length as a tuple"""
        length_resp = self._send_command(b'get_length\n')

        if len(length_resp) != 1:
            raise Exception('Wrong response when asked for stream length: {}'.format(length_resp))
        length = int(length_resp[0])

        time_resp = self._send_command(b'get_time\n')
        if len(time_resp) != 1:
            raise Exception('Wrong response when asked for elapsed time: {}'.format(time_resp))
        time = int(time_resp[0])

        return (time, length)

    def is_playing(self):
        """
        Returns True if stream is playing"""
        resp = self._send_command(b'is_playing\n')
        if len(resp) != 1:
            raise Exception('Wrong response when asked if playing: {}'.format(time_resp))
        return int(resp[0]) > 0

    def add(self, filename):
        """
        Adds a file to the playlist"""
        resp = self._send_command(b'add ' + filename.encode('utf-8') + b'\n')
        return resp

    def play(self):
        """
        Starts playback"""
        resp = self._send_command(b'play\n')
        return resp

    def stop(self):
        """
        Stops playback"""
        resp = self._send_command(b'stop\n')
        return resp

    def quit(self):
        """
        Closes VLC"""
        return self._send_command(b'quit\n')

    def __exit__(self):
        self.quit()
        self.sock.close()
