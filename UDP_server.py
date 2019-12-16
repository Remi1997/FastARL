import socket
import sys
import os
from io import BytesIO

# Create a UDP socket
UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 5001
socket_syn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mtu=1500
tab_segments= []

socket_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socket_syn.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

print ("Bind succeeded")

#sent = socket_syn.sendto("SYN".encode(),(UDP_IP_ADDRESS, UDP_PORT_NO))
while 1:
    (message, addrclt) = socket_syn.recvfrom(3)
    message= message.decode()
    print ("message:", message)
    if message == "SYN":
        message = "SYN-ACK7000".encode()
        socket_syn.sendto(message, addrclt)

    (message, addrclt) = socket_syn.recvfrom(3)
    message= message.decode()
    if message=="ACK":
        socket_syn.close()
        break
socket_data.bind((UDP_IP_ADDRESS, 7000))
fichierrecu= socket_data.recv(mtu).decode()
print(fichierrecu)
f = open("fichiertest.txt", 'w')
#------------------------------------------------- PARTIE A REFAIRE-----------------------
print(os.path.getsize(fichierrecu))
print(size)
for i in range (size):
    data=f.read(1500)
    numseq= 00000 + int(i)
    tab_segments.append(str(numseq)+data)
    print(tab_segments)

f.close()
