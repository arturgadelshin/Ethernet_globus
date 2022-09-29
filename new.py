import socket
import parsing_ethernet
host = '192.168.0.1'

port = 1233

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#msg = hex(500010000)
msg = "\x02\x00\x05\x00\x01\x00\x00"
print(msg.encode('utf-8'))
client.sendto(msg.encode('utf-8'), (host, port))

d = client.recvfrom(1024)
reply = d[0]
addr = d[1]
print(reply)
print(addr)

client.close()