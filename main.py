import socket
import struct
from multiprocessing.pool import ThreadPool
import datetime
import argparse
THREAD = 10
CHUNK = 1024
TIME = datetime.datetime(1900, 1, 1)


class DeceitfulServer:
    def __init__(self, delay, host='127.0.0.1', port=123):
        self._port = port
        self._host = host
        self._delay = delay
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((host, self._port))

    def start(self, input_packet, address):
        answer = self.packet(input_packet, self.get_bytes())
        self._sock.sendto(answer + self.get_bytes(), address)

    def get_bytes(self):
        time = (datetime.datetime.utcnow() - TIME).total_seconds() + self._delay
        seconds, mil_seconds = [int(x) for x in str(time).split('.')]
        return struct.pack('!II', seconds, mil_seconds)

    def packet(self, input_packet, come_time):
        return struct.pack('!B', 28) + struct.pack('!B', 1) \
               + struct.pack('!b', 0) + struct.pack('!b', -20) + struct.pack('!i', 0) \
               + struct.pack('!i', 0) + struct.pack('!i', 0) \
               + self.get_bytes() + input_packet[40:48] + come_time

    def work(self):
        while True:
            data, address = self._sock.recvfrom(CHUNK)
            print(f'{address} accept to {self._host}:{self._port}')
            ThreadPool(THREAD).apply_async(self.start, args=(data, address))


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delay', type=int, default=0, help='shift')
    parser.add_argument('-p', '--port', type=int, default=123, help='port listening')
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = arguments()
        DeceitfulServer(args.delay, port=args.port).work()
    except KeyboardInterrupt:
        exit(0)
