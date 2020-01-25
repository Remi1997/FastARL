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
    UDP_IP_ADDRESS = "0.0.0.0"
    UDP_PORT_NO = int(sys.argv[1])
    socket_syn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mtu=1500-6 # -6 car 6 est la taille de notre numéro de séquence il faut donc l'inclure dans la taille totale de ce qu'on envoie
    #tab_segments= []
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


    socket_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    socket_syn.bind((UDP_IP_ADDRESS, UDP_PORT_NO))



    #sent = socket_syn.sendto("SYN".encode(),(UDP_IP_ADDRESS, UDP_PORT_NO))
    while 1:
        (message, addrclt) = socket_syn.recvfrom(3)
        message= message.decode()
        print ("message:", message)
        if message == "SYN":
            socket_syn.sendto(b"SYN-ACK7000", addrclt)
            rtt1=time.time()

        (message, addrclt) = socket_syn.recvfrom(3)
        rtt2=time.time()
        message= message.decode()
        if message=="ACK":
            socket_syn.close()
            break
    socket_data.bind((UDP_IP_ADDRESS, 7000))
    print ("Entering UDP data transfer mode...")
    fichierrecu= socket_data.recv(mtu).decode() # pour que ça marche il faut mettre exactement la taille du buffer
    fichier= fichierrecu[0:-1]
    f=open(fichier,"rb")
    rtt=rtt2-rtt1
    print(rtt)
    socket_data.settimeout(rtt) #les fct bloquantes comme le receive ne le seront plus après ce paramètre
    #TRAITER LE CAS OU CEST UNE IMAGE
    f_size  = os.fstat(f.fileno()).st_size
    #-----------------------------------REMPLISSAGE DU TABLEAU DE SEGMENTS A ENVOYER--------------------------------------

    tab_segments= []
    while f.tell() < f_size:
        seq_number= get_numseq(j+1).encode() # en bytes
        tab_segments.append(seq_number+f.read(mtu)) # la taille devient 1506
        j+=1
    f.close()

    #----------------------------------- FIN REMPLISSAGE DU TABLEAU DE SEGMENTS A ENVOYER----------------


    #----------------------------------------ENVOI DU TABLEAU AU CLIENT ---------------------------------
    print("Sending data from file", fichierrecu,"to the client ...")
    print (len(tab_segments))
    current_segment=1
    sliding_window= 50
    total_segments= len(tab_segments)
    time1= time.time()
    list_ack_received=[]
    while current_segment < total_segments: #tant qu'on a pas atteint une valeur superieure au denrier segment
        for segment in tab_segments[current_segment-1:current_segment-1+sliding_window]:#on envoie tous les paquets de la sliding_window
            socket_data.sendto(segment, addrclt) #envoi de tous les segments du premier indice a l'indice+sliding sliding_window
#------------------------ TRAITEMENT DES ACK-----------------------------------

        for segment in tab_segments[current_segment-1:current_segment-1+sliding_window]:#on envoie tous les paquets de la sliding_window
            try:
                list_ack_received.append(int(socket_data.recv(9).decode()[3:9]))

            except socket.timeout:
                continue

        current_segment=max(list_ack_received)+1
        #else:
            #for segment in tab_segments[current_segment-1:current_segment-1+sliding_window]:
                #segment_formatted=int(segment[0:6].decode())
                #print("seg format",segment_formatted)
                #if segment_formatted not in list_ack_received:
                    #print("dans la boucle car pas recu ack")
                    #print("list ack received",list_ack_received)
                    #print ("list ack non received:", list_ack_non_received)
                    #print("segment pas recu:",segment_formatted)
                    #list_ack_non_received.append(segment_formatted) #si y a dautres segments non acquittés
                #if len(list_ack_non_received) >0:
                    #current_segment= min(list_ack_non_received)
                #else:

                #    list_ack_non_received.pop(list_ack_non_received.index(current_segment))
                #    print ("current segment qui renvoie seg perdu", current_segment)
                #if list_ack_received.count(segment_formatted) > 1: #si le segment quon vient de recevoir est 2 fois dans la liste des ack passer au segment suivant
                #    print("dans la boucle car ack répété")
                #    current_segment+=1
                #    break




#------------------------ FIN TRAITEMENT DES ACK--------------------------------


    #----------------------FIN DE TRANSFERT FICHIER---------------------------
    time2= time.time()

    print ("taille fichier: ",f_size)
    socket_data.sendto(b"FIN", addrclt)
    print("Data sent. End of communication.")
    bitrate= (f_size * 10**-6) / (time2-time1)
    print ("Bitrate:", round(bitrate,3),"Mo/s")
