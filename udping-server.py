import argparse
import socket, struct, time, random
from packet import *
from ctrl_c_handler import set_signal_handler

# Handle Ctrl-C
def signal_handler(signum, frame=None):
    exit(1)
set_signal_handler(signal_handler)

# Parse argument
parser = argparse.ArgumentParser()
parser.add_argument('server-address', nargs='?', metavar='server-address', default='0.0.0.0', help='Server address to bind. IPv4/IPv6 address. The default is 0.0.0.0')
parser.add_argument('-p', metavar='server-port', type=int, default=11888, help='Port to listen on. UDPing client must ping this port. The default is 11888.')
parser.add_argument('-v', action="store_true", help='Verbose mode. Display each UDPing request. The default is off.')
namespace = parser.parse_args()
args_dict = vars(namespace)

addr = args_dict['server-address']
port = args_dict['p']
is_verbose = args_dict['v']

# Bind address and port
print(f'UDPing Server is listening on port {addr} port {port} ...')
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((addr, port))

# Send UDP pongs
buffer = bytearray(65536)
buffer_view = memoryview(buffer)
while True:
    try:
        nbytes, addr = s.recvfrom_into(buffer, 65536)
        UDPingPacket.response_ping(buffer_view)
        s.sendto(buffer_view[:nbytes], addr)
        packet = UDPingPacket.from_bytes(buffer_view, nbytes)
        if is_verbose:
            print(f'Receiving from {addr[0]}:{addr[1]} seq={packet.index} nbytes={len(packet.payload)}({nbytes})')
    except ConnectionResetError as e:
        pass