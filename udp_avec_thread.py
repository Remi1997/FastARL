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
from multiprocessing import Value, Array
import sysv_ipc
#------------------------FONCTIONS ---------------------------------------------
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


def prepare_data(socket_data, mtu):
    mq = sysv_ipc.MessageQueue(128, sysv_ipc.IPC_CREAT)
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
    print ("Preparing the file to upload...")
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

    message = tab_segments.encode()
    mq.send(message)


#----------------------------------- FIN REMPLISSAGE DU TABLEAU DE SEGMENTS A ENVOYER----------------


#----------------------------------FIN FONCTIONS ---------------------------------------------
# Create a UDP socket
UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = int(sys.argv[1])
socket_syn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mtu=1500-6 # -6 car 6 est la taille de notre numéro de séquence il faut donc l'inclure dans la taille totale de ce qu'on envoie
#tab_segments= []
i=1
j=0

socket_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socket_syn.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

print ("Bind succeeded")

socket_data.settimeout(0.0230) #les fct 0.0230 bloquantes comme le receive ne le seront plus après ce paramètre

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
thread = threading.Thread(target=prepare_data, args=(socket_data,mtu))
thread.start()



#----------------------------------------ENVOI DU TABLEAU AU CLIENT ---------------------------------
print("Sending data from file", fichierrecu,"to the client ...")

current_segment=1
sliding_window= 70 #le max chercher
list_ack_received=[]

thread.join()
message, t = mq.receive()
tab_segments = message.decode()
total_segments= len(tab_segments)

time1= time.time()

while current_segment < total_segments: #tant qu'on a pas atteint une valeur superieure au denrier segment
    if total_segments - current_segment <  sliding_window: #retrecir la window car on a - que le window length qui nous reste
      sliding_window = total_segments- current_segment +1 #taille de la fenetre restante

    for segment in tab_segments[current_segment-1:current_segment-1+sliding_window]:#on envoie tous les paquets de la sliding_window
        socket_data.sendto(segment, addrclt) #envoi de tous les segments du premier indice a l'indice+sliding sliding_window
    for i in range (sliding_window):#on envoie tous les paquets de la sliding_window
        try:
            list_ack_received.append(int(socket_data.recv(9).decode()[3:9]))
        except socket.timeout: #si je ne recois pas le ack au bout de x temps je fais ca
            pass
    for segment2 in tab_segments[current_segment-1:current_segment-1+sliding_window]:#on envoie tous les paquets de la sliding_window
        number_seg= int(segment2[0:6].decode())
        if  list_ack_received.count(number_seg) >= 2: #FAST RETRANSMIT, 2 au lieu de 4 comme indiqué dns RFC
            socket_data.sendto(segment2, addrclt) #envoi de tous les segments du premier indice a l'indice+sliding sliding_window
        if number_seg not in list_ack_received:
            current_segment = int(segment2[0:6].decode())
            pass
        else:
            current_segment+= 1

    print(list_ack_received)
    print(current_segment)

#----------------------FIN DE TRANSFERT FICHIER---------------------------
time2= time.time()
socket_data.sendto(b"FIN", addrclt)
print("Data sent. End of communication.")
print ("taille fichier: ",f_size)
bitrate= (f_size * 10**-6) / (time2-time1)
print ("Bitrate:", round(bitrate,3),"Mo/s")

f.close()