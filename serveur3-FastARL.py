import socket
import sys
import os
import signal
import time
from subprocess import Popen, PIPE
import math
import threading


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

def connection_client(UDP_IP_ADDRESS,count,addrclt,rtt,port):
        socket_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #en ouvrir plusieurs par client
        mtu=1500-6 # -6 car 6 est la taille de notre numéro de séquence il faut donc l'inclure dans la taille totale de ce qu'on envoie
        #tab_segments= []
        i=1
        j=0
        socket_data.bind((UDP_IP_ADDRESS,port+count))
        fichierrecu= socket_data.recv(mtu).decode() # pour que ça marche il faut mettre exactement la taille du buffer
        fichier= fichierrecu[0:-1]
        f=open(fichier,"rb")
        #TRAITER LE CAS OU CEST UNE IMAGE
        f_size  = os.fstat(f.fileno()).st_size
    #-----------------------------------REMPLISSAGE DU TABLEAU DE SEGMENTS A ENVOYER--------------------------------------
    #----------Garder en cache quand un client demande le meme fichier = plus haut debit ---------------------------------------------------
        tab_segments=[]
        while f.tell() < f_size:
            seq_number= get_numseq(j+1).encode() # en bytes
            tab_segments.append(seq_number+f.read(mtu)) # la taille devient 1506
            j+=1
        f.close()

    #----------------------------------- FIN REMPLISSAGE DU TABLEAU DE SEGMENTS A ENVOYER----------------#

        socket_data.settimeout(rtt) #les fct 0.0230 bloquantes comme le receive ne le seront plus après ce paramètre
   #----------------------------------------ENVOI DU TABLEAU AU CLIENT ---------------------------------
        current_segment=1
        sliding_window= 25
        total_segments= len(tab_segments)
        time1= time.time()
        list_ack_received=[]


        while current_segment < total_segments: #tant qu'on a pas atteint une valeur superieure au denrier segment
            #if current_segment > total_segments - sliding_window: #retrecir la window car on a - que le window length qui nous reste
             #   sliding_window = total_segments- current_segment #taille de la fenetre restante
            for segment in tab_segments[current_segment-1:current_segment-1+sliding_window]:#on envoie tous les paquets de la sliding_window
                socket_data.sendto(segment, addrclt) #envoi de tous les segments du premier indice a l'indice+sliding sliding_window
    #------------------------ TRAITEMENT DES ACK-----------------------------------
                        #on envoie tous les paquets de la sliding_window
                try:
                    list_ack_received.append(int(socket_data.recv(9).decode()[3:9]))

                except socket.timeout:
                    continue
            if len(list_ack_received) >0:
                current_segment=max(list_ack_received)+1



#------------------------ FIN TRAITEMENT DES ACK--------------------------------

        #----------------------FIN DE TRANSFERT FICHIER---------------------------
        time2= time.time()
        socket_data.sendto(b"FIN", addrclt)
        #bitrate= (f_size * 10**-6) / (time2-time1)
        #print ("Bitrate:", round(bitrate,3),"Mo/s")


if __name__ == '__main__':
    # Create a UDP socket
    tab_segments= []
    UDP_IP_ADDRESS = "0.0.0.0"
    UDP_PORT_NO = int(sys.argv[1])
    socket_syn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_syn.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
    count=0
    while True:
            syn, addrclt =socket_syn.recvfrom(3)
            count+=1
            synack="SYN-ACK" +str(int(sys.argv[1])+count)
            socket_syn.sendto(synack.encode(), addrclt)
            rtt1=time.time()
            (message, addrclt) = socket_syn.recvfrom(3)
            rtt2=time.time()
            rtt=rtt2-rtt1
            message= message.decode()
            newthread = threading.Thread(target=connection_client, args=(UDP_IP_ADDRESS,count, addrclt,rtt,int(sys.argv[1])))
            newthread.start()
