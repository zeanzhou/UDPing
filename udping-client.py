import argparse
import socket, struct, itertools, time, statistics
from threading import Event, Thread
from packet import *
from ctrl_c_handler import set_signal_handler

# For compatibility
try:
    time.time_ns()
except AttributeError:
    time.time_ns = lambda: int(time.time()*1_000_000_000)

# Handle Ctrl-C
EXIT = Event()
def signal_handler(signum, frame=None):
    print()
    if not EXIT.is_set():
        # print(' UDPing exiting...')
        EXIT.set()
    else:
        # print(' UDPing exits forcefully.')
        exit(1)
    return 1
set_signal_handler(signal_handler)

# Parse argument
parser = argparse.ArgumentParser()
parser.add_argument('host', metavar='server-address', help='Destination host name. Either domain name or IPv4/IPv6 address.')
parser.add_argument('-p', metavar='server-port', type=int, default=11888, help='Destination port number. UDPing server must listen on this port. The default is 11888.')
parser.add_argument('-W', metavar='timeout', type=float, default=2.0, help='Time to wait for a response, in seconds. The default is 2.0.')
parser.add_argument('-s', metavar='packetsize', type=int, default=32, help=f'Specifies the number of data bytes to be sent, including header. The default is 32, the acceptable range is from {HEADER_LENGTH} to 65507 bytes.')
parser.add_argument('-i', metavar='interval', type=float, default=1.0, help='Time to wait between sending each packet. The default is 1.0.')
parser.add_argument('-c', metavar='count', type=int, default=-1, help='Stop after sending count packets. The default is -1, meaning that it keeps sending forever.')
parser.add_argument('-q', action="store_true", help='Quiet output. Nothing is displayed except the summary lines at startup time and when finished.')
namespace = parser.parse_args()
args_dict = vars(namespace)

# Read arguments
host = args_dict['host']
port = args_dict['p']
timeout = args_dict['W']
packetsize = min(max(args_dict['s'], HEADER_LENGTH), 65507)
interval = args_dict['i']
count = args_dict['c']
quiet = args_dict['q']
ip = socket.gethostbyname(host)
sequence = itertools.count() if count==-1 else range(count)

# Set up UDP port
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(timeout)

# Send UDP pings
try:
    print(f'UDP Pinging {host} ({ip}) with {packetsize-HEADER_LENGTH}({packetsize}) bytes of data:')
    delay = []
    transmitted = 0
    loss = 0
    for i in sequence:
        payload = bytes((i % 256,))*(packetsize-HEADER_LENGTH)
        for _ in range(1):
            byte = None

            # Construct & Send Ping Packet
            t1 = time.time_ns()
            packet_ping = UDPingPacket.create(UDPingPacket.TYPE_PING, t1, i, payload)
            s.sendto(packet_ping.to_bytes(), (ip, port))
            transmitted += 1

            # Keep trying if the incoming packet is invalid/outdated
            while (time_passed := (time.time_ns() - t1)/1_000_000_000) < timeout:
                s.settimeout(timeout - time_passed)

                # Receive Pong Packet
                result = 'Port is open'
                try:
                    byte, addr = s.recvfrom(65536)
                except socket.timeout:
                    result = 'No response '
                
                # Stop timing
                t2 = time.time_ns()
                timediff_ns = t2 - packet_ping.timestamp
                timediff_ms = int(timediff_ns / 1000) / 1000

                # Parse Pong Packet
                if byte:
                    # Invalid format
                    try:
                        packet_pong = UDPingPacket.from_bytes(byte)
                    except:
                        continue

                    # Outdated index
                    if (packet_pong.index != packet_ping.index):
                        continue

                    # Wrong type (packet might be forwarded back directly)
                    if (packet_pong.type != UDPingPacket.TYPE_PONG):
                        continue

                    # Successful ping, stop trying
                    break
            
            # Output for each ping
            if not quiet:
                print(f"Probing {ip}:{port}/udp - {result} - seq={packet_ping.index} time={timediff_ms}ms")

            if result == 'Port is open':
                delay.append(timediff_ms)
            else:
                loss += 1

        # Interruptible sleep
        EXIT.wait(interval)
        if EXIT.is_set():
            break

finally:
    s.close()
    if (transmitted > 0):
        print(f'--- {ip}:{port}  udp ping statistics ---')
        print(f'{transmitted} packets transmitted, {len(delay)} packets received, \
{round(loss/transmitted*100, 1)}% packet loss')
    if len(delay) > 1:
        print(f'rtt min/avg/max/mdev = {min(delay)}/{round(statistics.mean(delay), 3)}\
/{max(delay)}/{round(statistics.stdev(delay), 3)}ms')