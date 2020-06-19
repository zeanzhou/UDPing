from collections import namedtuple
import struct, time
HEADER_FORMAT = '!ccQI'
HEADER_LENGTH = struct.calcsize(HEADER_FORMAT)

_UDPingPacket = namedtuple('UDPingPacket', ['version', 'type', 'timestamp', 'index', 'payload'])

class UDPingPacket(_UDPingPacket):
    TYPE_PING = bytes((0x01,))
    TYPE_PONG = bytes((0x02,))
    PROTO_VERSION = bytes((0x01,))

    @staticmethod
    def create(type, timestamp, index, payload=b''):
        return UDPingPacket(UDPingPacket.PROTO_VERSION, type, timestamp, index%4294967295, payload)

    @staticmethod
    def from_bytes(byte, length=None):
        if length is None:
            length = len(byte)
        if length < HEADER_LENGTH:
            raise RuntimeError('Packet header too small.')
        return UDPingPacket(
            *struct.unpack(HEADER_FORMAT, byte[:HEADER_LENGTH]),
            *struct.unpack(f'!{length-HEADER_LENGTH}s', byte[HEADER_LENGTH:length])
        )
    
    @staticmethod
    def response_ping(buffer: memoryview):
        buffer[1] = UDPingPacket.TYPE_PONG[0]

    def to_bytes(self):
        return struct.pack(HEADER_FORMAT+f'{len(self.payload)}s', *self)
    

        
# buf = struct.pack('!ccQi', bytes((0x0A,)), bytes((0x01,)), time.time_ns(), 255)
# print(buf+b'\xFF')
# print(UDPingPacket.from_bytes(buf+b'\xFF').to_bytes())