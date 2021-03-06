
import socket

msg = \
    'M-SEARCH * HTTP/1.1\r\n' \
    'HOST:239.255.255.250:1900\r\n' \
    'ST:upnp:rootdevice\r\n' \
    'MX:2\r\n' \
    'MAN:"ssdp:discover"\r\n' \
    '\r\n'

# Set up UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.settimeout(2)
s.sendto(msg.encode("utf8"), ('239.255.255.250', 1900) )
print("------------ Started -------------")
try:
    while True:
        data, addr = s.recvfrom(65507)
        print(f" --  {addr}  --\n{data.decode('utf8')}")
except socket.timeout:
    pass
print("------------- Done -----------")