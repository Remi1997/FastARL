import socket
import sys
import os
import signal
import time
from io import BytesIO
from PIL import Image
from subprocess import Popen, PIPE
# Create a UDP socket
UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 5001
socket_syn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mtu=1500 -6 # -6 car 6 est la taille de notre numéro de séquence il faut donc l'inclure dans la taille totale de ce qu'on envoie
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

print ("Bind succeeded")

socket_data.settimeout(1) #les fct bloquantes comme le receive ne le seront plus après ce paramètre

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
print ("Entering UDP data transfer mode...")
fichierrecu= socket_data.recv(mtu).decode() # pour que ça marche il faut mettre exactement la taille du buffer
fichier= fichierrecu[0:-1]
f=open(fichier,"rb")

#TRAITER LE CAS OU CEST UNE IMAGE
f_size  = os.fstat(f.fileno()).st_size
#-----------------------------------REMPLISSAGE DU TABLEAU DE SEGMENTS A ENVOYER--------------------------------------

# essayer cette méthode
#data = f.read()
#tab_segments.append(data%mtu)
tab_segments= []
while f.tell() < f_size:
    length_left= f_size-f.tell()
    seq_number= get_numseq(j+1).encode() # en bytes
    tab_segments.append(seq_number)
    if length_left >=mtu:
        for k in range (mtu): #ajouter 1 octet jusqua arriver à mtu
            lecture = f.read(1)
            tab_segments[j]+= lecture
    else:
        for k in range(length_left):
            lecture = f.read(1)
            tab_segments[j]+=lecture
    j+=1




print("LE TABLEAU EST:", tab_segments)

print ("longueur du tab: ", len(tab_segments))


#----------------------------------- FIN REMPLISSAGE DU TABLEAU DE SEGMENTS A ENVOYER----------------


#----------------------------------------ENVOI DU TABLEAU AU CLIENT ---------------------------------
print("Sending data from file", fichierrecu,"to the client ...")
k=0
time1= time.time()
while k<len(tab_segments):
    socket_data.sendto(tab_segments[k], addrclt)
    try:
        ack_received= socket_data.recv(9).decode() #essayer de recevoir le ack
    except socket.timeout: # si on l'a pas reçu au bout de 5 sec
        continue #refaire la boucle
    finally:
        if len(ack_received) == 9:
            ack_received= ack_received[3:9] # on reçoit ACK0000N il faut extraire les 6 derniers elements
            if ack_received == tab_segments[k][0:6].decode(): # si le client a bien acquitté le dernier segment reçu, incrementer j pour envoyer le prochain segment
                k+=1

#----------------------FIN DE TRANSFERT FICHIER---------------------------
time2= time.time()
socket_data.sendto(b"FIN", addrclt)
print("Data sent. End of communication.")
print ("taille fichier: ",f_size)
bitrate= (f_size *8 * 10**-6) / (time2-time1)
print ("Bitrate:", round(bitrate,3),"Mbps")

f.close()
