import socket
import sys

# Create a UDP socket
UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 3000
socket_syn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


socket_syn.bind((UDP_IP_ADDRESS, UDP_PORT_NO))


#sent = socket_syn.sendto("SYN".encode(),(UDP_IP_ADDRESS, UDP_PORT_NO))
while 1:
    received= socket_syn.recv(3)
    received.decode()
    print(received)
    if received =="SYN":
        sent = socket_syn.sendto("SYN-ACK7000".encode(), (UDP_IP_ADDRESS, UDP_PORT_NO))
