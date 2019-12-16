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
i=1
j=0

socket_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socket_syn.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

print ("Bind succeeded")

#sent = socket_syn.sendto("SYN".encode(),(UDP_IP_ADDRESS, UDP_PORT_NO))
while 1:
    (message, addrclt) = socket_syn.recvfrom(3)
    message= message.decode()
    print ("message:", message)
    if message == "SYN":
        socket_syn.sendto(b"SYN-ACK7000", addrclt)

    (message, addrclt) = socket_syn.recvfrom(3)
    message= message.decode()
    if message=="ACK":
        socket_syn.close()
        break
socket_data.bind((UDP_IP_ADDRESS, 7000))
fichierrecu= socket_data.recv(mtu).decode()
f = open("fichiertest.txt", 'r+')
f_size  = os.fstat(f.fileno()).st_size
print ("taille fichier: ",f_size)
#-----------------------------------REMPLISSAGE DU TABLEAU DE SEGMENTS A ENVOYER-----------------------

while f.tell() < f_size:
    data=f.read(1500)
    if len(str(i))==1:
        numseq= "00000" + str(i)
    if len(str(i))==2:
        numseq= "0000" + str(i)
    if len(str(i))==3:
        numseq= "000" + str(i)
    if len(str(i))==4:
        numseq= "00" + str(i)
    if len(str(i))==5:
        numseq= "0" + str(i)
    if len(str(i))==6:
        numseq= str(i)
    tab_segments.append(numseq+data)
    i+=1
print ("longueur du tab: ", len(tab_segments))
#----------------------------------------ENVOI DU TABLEAU AU CLIENT ---------------------------------
while j<len(tab_segments):
    socket_data.sendto(tab_segments[j].encode(), addrclt)
    ack_received= socket_data.recv(9).decode()
    ack_received= ack_received[3:9] # on reçoit ACK0000N il faut extraire les 6 derniers elements
    if ack_received == tab_segments[j][0:6]: # si le client a bien acquitté le dernier segment reçu, incrementer j pour envoyer le prochain segment
        j+=1
    #else:
        #SET UN TIMER PUIS RENVOYER
#----------------------FIN DE TRANSFERT FICHIER---------------------------
socket_data.sendto(b"FIN", addrclt)



f.close()
