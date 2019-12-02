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
  char *monfichier;
  int i = 1; //num seq initial

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
    fptr=fopen("fichiertest.txt","rb");
    stat("fichiertest.txt", &st);
    int filesize = st.st_size; //taille du fichier
    printf("taille du fichier: %d\n",filesize);
    int currentsize=0;
    char *contenufichier = malloc(filesize * sizeof(int));
    char *segmentsaenvoyer = malloc(filesize * sizeof(int));
    fgets( contenufichier, filesize, fptr ); //prend que le 1 er paragraphe probleme
    do
    {
      char numseq= i+currentsize;
      memcpy(&numseq+segmentsaenvoyer,contenufichier+currentsize, MTU);
      printf("%s", segmentsaenvoyer);
      sendto(server_desc_data, (char *) segmentsaenvoyer, MTU+4,
      MSG_CONFIRM, (const struct sockaddr *) &client,
            len);
      currentsize += MTU;




      printf("%s\n", segmentsaenvoyer);

    } while (currentsize <= filesize);


    /*fgets ( monfichier, 100, fptr ); // transmet les 0 à 99 premiers elements

    tabsegments[i] += i,monfichier;
    i+=1;
    printf("info %d\n", tabsegments[i]);*/

    //chaque elt du tableau doit etre envoyé et si c fini envoyer
    // fin recevoir ack du fin puis close socket






    free(contenufichier);
    free(segmentsaenvoyer);
    fclose (fptr);





















  }

close(server_desc);
return 0;
}
