# UDPing
A simple UDP ping tool written in Python

## Usage

### Server

    udping-server.py [-h] [-p server-port] [-v] [server-address]

    positional arguments:
    server-address  Server address to bind. IPv4/IPv6 address. The default is 0.0.0.0

    optional arguments:
    -h, --help      show this help message and exit
    -p server-port  Port to listen on. UDPing client must ping this port. The default is 11888.
    -v              Verbose mode. Display each UDPing request. The default is off.

### Client

    udping-client.py [-h] [-p server-port] [-W timeout] [-s packetsize] [-i interval] [-c count] [-q]
                     server-address

    positional arguments:
    server-address  Destination host name. Either domain name or IPv4/IPv6 address.

    optional arguments:
    -h, --help      show this help message and exit
    -p server-port  Destination port number. UDPing server must listen on this port. The default is 11888.
    -W timeout      Time to wait for a response, in seconds. The default is 2.0.
    -s packetsize   Specifies the number of data bytes to be sent, including header. The default is 32, the
                    acceptable range is from 14 to 65507 bytes.
    -i interval     Time to wait between sending each packet. The default is 1.0.
    -c count        Stop after sending count packets. The default is -1, meaning that it keeps sending forever.
    -q              Quiet output. Nothing is displayed except the summary lines at startup time and when finished.

## Example

```bash
python udping-server.py
```

```bash
python udping-client.py 127.0.0.1
```

## More Examples

#### Test the latency when sending large UDP packets over specfic port

```bash
# Listen on UDP port 12345 for all interfaces on this host
python udping-server.py -p 12345
```

```bash
# Send UDP pings to 10.11.12.13:12345 with packet size 65500 bytes
python udping-client.py 10.11.12.13 -p 12345 -s 65500
```

#### Test the latency when extremely large delay happens

```bash
# Listen on UDP port 11888 for all interfaces on this host, verbose on
# With verbose on, you can decide whether a packet arrived or not.
# Another way is to increase the timeout at the client side.
python udping-server.py -v
```

```bash
# Send UDP pings to [server]:12345 with timeout 3.5s every 2s
# Client sleeps for 2s after the last ping timed out or succeeded
python udping-client.py [server] -W 3.5 -i 2.0
```

## Reference

This project is inspired by  [TCPing](https://www.elifulkerson.com/projects/tcping.php) and [ping](https://linux.die.net/man/8/ping). The argument definitions and the output format take both as a reference.