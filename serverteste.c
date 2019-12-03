#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/stat.h>

#define MAXLINE 1024
#define MTU 22

int main (int argc, char *argv[]) {

  struct sockaddr_in adresse, client, adressedata;
  int port= 5001;
  int valid= 1;
  socklen_t alen= sizeof(client);
  char buffer[MAXLINE];
  int n;
  char *syn= "SYN\0";
  char *ack= "ACK\0";
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

      sendto(server_desc, (const char *)"SYN ACK,7000\0", strlen("SYN ACK,7000"),
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

    //PORT DE DONNEES
    sendto(server_desc_data, (const char *)"DEBUT ENVOI DU FICHIER\0", strlen("DEBUT ENVOI DU FICHIER\0"),
    MSG_CONFIRM, (const struct sockaddr *) &client,
          len);

    FILE * fptr;
    struct stat st;
    int caractere;
    int currentsize=0;
    fptr=fopen("fichiertest.txt","rb");
    stat("fichiertest.txt", &st);
    int filesize = st.st_size; //taille du fichier
    printf("taille du fichier: %d\n",filesize);

    char *segmentsaenvoyer = malloc(filesize * sizeof(int)); //vider le buffer c'est mieux
    //int numseq= 000001; // 1 octet après le ack
    //char numseqatransmettre[6];
    //sprintf(numseqatransmettre, "%d", numseq);
    //printf("%s\n", numseqatransmettre);

    do
    {
      int lus= fread(segmentsaenvoyer, 1, MTU, fptr);
      sendto(server_desc_data, (char *) segmentsaenvoyer,lus,
      MSG_CONFIRM, (const struct sockaddr *) &client,
            len);
      currentsize += lus;
      printf("segment envoyé %s\n, current size %d\n",segmentsaenvoyer, currentsize);
    } while (currentsize< filesize) ;




    free(segmentsaenvoyer);
    fclose (fptr);



  }

close(server_desc);
return 0;
}
