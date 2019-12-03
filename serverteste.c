#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/stat.h>

#define MAXLINE 1024
#define MTU 1024

char *String_Concat (char *String_1, char *String_2)
{
    size_t len1 = strlen(String_1);
    size_t len2 = strlen(String_2);
    char *StringResult = malloc(len1+len2+1);
    //might want to check for malloc-error...
    memcpy(StringResult, String_1, len1);
    memcpy(&StringResult[len1], String_2, len2+1);
    return StringResult;
}
int main (int argc, char *argv[]) {

  struct sockaddr_in adresse, client, adressedata;
  int port= 5001;
  int valid= 1;
  socklen_t alen= sizeof(client);
  char buffer[MAXLINE];
  int n;
  char *syn= "SYN";
  char *ack= "ACK";
  //long long numseq= 000000;

  //create socket
  int server_desc = socket(AF_INET, SOCK_DGRAM, 0);

  //handle error
  if (server_desc < 0) {
    perror("Cannot create socket\n");
    return -1;
  }

  setsockopt(server_desc, SOL_SOCKET, SO_REUSEADDR, &valid, sizeof(int));

  adresse.sin_family= AF_INET;
  adresse.sin_port= htons(port);
  adresse.sin_addr.s_addr= htonl(INADDR_ANY);

    //initialize socket
  if (bind(server_desc, (struct sockaddr*) &adresse, sizeof(adresse)) == -1) {
    perror("Bind failed\n");
    close(server_desc);
    return -1;
  }

  int server_desc_data = socket(AF_INET, SOCK_DGRAM, 0);
  //handle error
  if (server_desc_data < 0) {
    perror("Cannot create socket\n");
    return -1;
  }
  setsockopt(server_desc_data, SOL_SOCKET, SO_REUSEADDR, &valid, sizeof(int));

  adressedata.sin_family= AF_INET;
  adressedata.sin_port= htons(7000);
  adressedata.sin_addr.s_addr= htonl(INADDR_ANY);


  //initialize socket
  if (bind(server_desc_data, (struct sockaddr*) &adressedata, sizeof(adressedata)) == -1) {
    perror("Bind failed\n");
    close(server_desc);
    return -1;
  }


  int len = sizeof(client);

  while (1) {

    n = recvfrom(server_desc, (char *)buffer, MAXLINE,
                MSG_WAITALL, ( struct sockaddr *) &client,
                &len);
    buffer[n] = '\0';
    if (strcmp(buffer,syn) == 0) {
      printf("Client : %s\n", buffer);

      sendto(server_desc, (const char *)"SYN-ACK7000", strlen("SYN ACK,7000"),
      MSG_CONFIRM, (const struct sockaddr *) &client,
            len);

    }
    else {
    close(server_desc);}
    n = recvfrom(server_desc, (char *)buffer, MAXLINE,
                MSG_WAITALL, ( struct sockaddr *) &client,
                &len);
    buffer[n] = '\0';
    if (strcmp(buffer,ack) == 0) {
      printf("Client : %s\n", buffer);
      printf("FIN DU THREE WAY HANDSHAKE\n" );}
    else {
    close(server_desc);}

    n = recvfrom(server_desc_data, (char *)buffer, MTU,
    MSG_WAITALL, ( struct sockaddr *) &client,
    &len);
    buffer[n] = '\0';
    FILE * fptr;
    struct stat st;
    int caractere;
    fptr=fopen(buffer,"rb");
    stat(buffer, &st);
    int filesize = st.st_size; //taille du fichier
    printf("taille du fichier: %d\n",filesize);

    char *segmentsaenvoyer = malloc(filesize * sizeof(int)); //vider le buffer c'est mieux
    long long numseq= 000000; // a revoir car commence par 0 6 octets pr le num de sequence
    char *segments= malloc(filesize * sizeof(int) + 7);
    char numseqstr[6];
    char numack[6];

    while (numseq<filesize){
      int lus= fread(segmentsaenvoyer, 1, MTU, fptr);
      sprintf(numseqstr, "%lld", numseq); //conversion int --> str
      segments=String_Concat(numseqstr,segmentsaenvoyer);

      sendto(server_desc_data, (char *) segments,strlen(numseqstr)+lus,
      MSG_CONFIRM, (const struct sockaddr *) &client,
            len);
//POUR RECEVOIR LE ACK00000N
      n = recvfrom(server_desc_data, (char *)buffer, 9,
      MSG_WAITALL, ( struct sockaddr *) &client,
      &len);
      buffer[n] = '\0';
      memcpy(numack, buffer+3, 9 );
      printf("NUMACK%s\n", numack);
      if (atoi(numack) == numseq){
        numseq+=lus;

      }
      printf("Client : %s\n", buffer);

}

sendto(server_desc_data, (char *) "FIN",strlen("FIN"),
MSG_CONFIRM, (const struct sockaddr *) &client,
      len);


    free(segmentsaenvoyer);
    fclose (fptr);



  }

close(server_desc);
return 0;
}
