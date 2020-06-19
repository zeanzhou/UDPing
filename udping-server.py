import socket, struct, time, random
from packet import *

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 11888))

buffer = bytearray(65536)
buffer_view = memoryview(buffer)
while True:
    try:
        nbytes, addr = s.recvfrom_into(buffer, 65536)
        UDPingPacket.response_ping(buffer_view)
        s.sendto(buffer_view[:nbytes], addr)
        packet = UDPingPacket.from_bytes(buffer_view, nbytes)
        print(f'Receiving from {addr[0]}:{addr[1]} seq={packet.index} nbytes={len(packet.payload)}({nbytes})')
    except ConnectionResetError as e:
        pass