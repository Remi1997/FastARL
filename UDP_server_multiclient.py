import socket
import sys
import os
import signal
import time
from io import BytesIO
from PIL import Image
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

def connection_client(port):
        print(port)
        socket_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #en ouvrir un par client
        mtu=1500-6 # -6 car 6 est la taille de notre numéro de séquence il faut donc l'inclure dans la taille totale de ce qu'on envoie
        #tab_segments= []
        i=1
        j=0
        socket_data.bind(('',port))
        print ("Entering UDP data transfer mode...")
        fichierrecu= socket_data.recv(mtu).decode() # pour que ça marche il faut mettre exactement la taille du buffer
        fichier= fichierrecu[0:-1]
        f=open(fichier,"rb")
        #TRAITER LE CAS OU CEST UNE IMAGE
        f_size  = os.fstat(f.fileno()).st_size
        #-------------------
        socket_data.settimeout(0.0230) #les fct 0.0230 bloquantes comme le receive ne le seront plus après ce paramètre
#-----------------------------------REMPLISSAGE DU TABLEAU DE SEGMENTS A ENVOYER--------------------------------------
        tab_segments=[]
        while f.tell() < f_size:
            seq_number= get_numseq(j+1).encode() # en bytes
            tab_segments.append(seq_number+f.read(1500))
            j+=1
        f.close()

    #----------------------------------- FIN REMPLISSAGE DU TABLEAU DE SEGMENTS A ENVOYER----------------#


        #----------------------------------------ENVOI DU TABLEAU AU CLIENT ---------------------------------
        print("Sending data from file", fichierrecu,"to the client ...")

        current_segment=1
        sliding_window= 20
        total_segments= len(tab_segments)
        print(total_segments)
        time1= time.time()
        list_ack_received=[]

        while current_segment < total_segments: #tant qu'on a pas atteint une valeur superieure au denrier segment
            if current_segment > total_segments - sliding_window: #retrecir la window car on a - que le window length qui nous reste
                sliding_window = total_segments- sliding_window #taille de la fenetre restante
            for segment in tab_segments[current_segment-1:current_segment-1+sliding_window]:#on envoie tous les paquets de la sliding_window
                socket_data.sendto(segment, addrclt) #envoi de tous les segments du premier indice a l'indice+sliding sliding_window

            for segment in tab_segments[current_segment-1:current_segment-1+sliding_window]:#on envoie tous les paquets de la sliding_window
                try:
                    list_ack_received.append(int(socket_data.recv(9).decode()[3:9]))
                except socket.timeout:
                    continue

            current_segment=max(list_ack_received)+1





        #----------------------FIN DE TRANSFERT FICHIER---------------------------
        time2= time.time()
        socket_data.sendto(b"FIN", addrclt)
        print("Data sent. End of communication.")
        print ("taille fichier: ",f_size)
        bitrate= (f_size * 10**-6) / (time2-time1)
        print ("Bitrate:", round(bitrate,3),"Mo/s")
        f.close()

# Create a UDP socket
if __name__ == "__main__":
    UDP_IP_ADDRESS = "0.0.0.0"
    UDP_PORT_NO = int(sys.argv[1])
    socket_syn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    threads=[]
    socket_syn.bind(('', UDP_PORT_NO))
    port=7001

    while True:
            syn, addrclt =socket_syn.recvfrom(3)
            syn= syn.decode()
            if syn=="SYN":
                synack="SYN-ACK" +str(port+1)
                print ("Bind succeeded")
                socket_syn.sendto(synack.encode(), addrclt)
                (message, addrclt) = socket_syn.recvfrom(3)
                message= message.decode()
                if message=="ACK":
                    print("Three way handshake done")
                    port+=1
                    newthread = threading.Thread(target=connection_client, args=(port,))
                    newthread.start()
                    threads.append(newthread)
