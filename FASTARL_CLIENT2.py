import socket
import sys
import os
import signal
import time
from io import BytesIO
from PIL import Image
from subprocess import Popen, PIPE
import math
# Create a UDP socket
while 1:
    UDP_IP_ADDRESS = "0.0.0.0" #Localhost
    UDP_PORT_NO = int(sys.argv[1])
    socket_syn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mtu=1500-6
    i=1
    j=0

    def get_numseq(i): #pour avoir le format: 00000i
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
        return numseq



    socket_syn.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
    while 1:
        socket_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        (message, addrclt) = socket_syn.recvfrom(3)
        message= message.decode()
        socket_syn.sendto(b"SYN-ACK7000", addrclt)
        rtt1=time.time()
        (message, addrclt) = socket_syn.recvfrom(3)
        rtt2=time.time()
        message= message.decode()
        socket_data.bind((UDP_IP_ADDRESS, 7000))
        fichierrecu= socket_data.recv(mtu).decode()
        fichier= fichierrecu[0:-1]
        f=open(fichier,"rb")
        rtt=rtt2-rtt1
        socket_data.settimeout(2*(rtt2-rtt1))
        f_size  = os.fstat(f.fileno()).st_size
        #----------------------REMPLISSAGE DU TABLEAU DE SEGMENTS A ENVOYER---------
        tab_segments= []
        while f.tell() < f_size:
            seq_number= get_numseq(j+1).encode()
            tab_segments.append(seq_number+f.read(mtu))
            j+=1
        f.close()

        #----------------------------------- FIN REMPLISSAGE DU TABLEAU DE SEGMENTS A ENVOYER-----

        #------------------------------------ ENVOI DU TABLEAU AU CLIENT -------------------------
        current_segment=1
        sliding_window= 70 # paramètre à changer pour les test
        list_ack_received=[]
        while current_segment < len(tab_segments): #tant qu'on a pas atteint une valeur superieure au denrier segment
            for segment in tab_segments[current_segment-1:current_segment-1+sliding_window]:#on envoie tous les paquets de la sliding_window
                socket_data.sendto(segment, addrclt) #envoi de tous les segments du premier indice a l'indice+sliding sliding_window
                rtt1=time.time()
#------------------------ TRAITEMENT DES ACK-----------------------------------
                try:
                    list_ack_received.append(int(socket_data.recv(9).decode()[3:9]))
                    rtt2=time.time()
                    socket_data.settimeout(2*(rtt2-rtt1))
                except socket.timeout:
                    continue
            current_segment=max(list_ack_received)+1
        #------------------------------------ FIN TRAITEMENT DES ACK-------------------------------
        socket_data.sendto(b"FIN", addrclt)
        socket_data.close()
