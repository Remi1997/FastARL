#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define MAXLINE 1024

int main (int argc, char *argv[]) {

  struct sockaddr_in adresse;
  int port = 5001;
  int valid = 1;
  char buffer[22+6];
  char *syn_ack= "SYN ACK\0";

  //create socket
  int server_desc = socket(AF_INET, SOCK_DGRAM, 0);

  // handle error
  if (server_desc < 0) {
    perror("cannot create socket\n");
    return -1;
  }

  setsockopt(server_desc, SOL_SOCKET, SO_REUSEADDR, &valid, sizeof(int));

  adresse.sin_family= AF_INET;
  adresse.sin_port= htons(port);
  adresse.sin_addr.s_addr= htonl(INADDR_LOOPBACK);


    int n, len;
    len = sizeof(adresse);
        sendto(server_desc, (const char *)"SYN\0", strlen("SYN"),
            MSG_CONFIRM, (const struct sockaddr *) &adresse,
                len);


  while (1){
                n = recvfrom(server_desc, (char *)buffer, MAXLINE,
                            MSG_WAITALL, ( struct sockaddr *) &adresse,
                            &len);
                buffer[n] = '\0';
                char *token;

                /* get the first token */
                token = strtok(buffer, ",");

                if (strcmp(token,syn_ack) == 0) {
                  printf("Server : %s\n", buffer);

                  sendto(server_desc, (const char *)"ACK\0", strlen("ACK"),
                  MSG_CONFIRM, (const struct sockaddr *) &adresse,
                        len);
                  buffer[n] = '\0';
                  token = strtok(NULL, ",");
                  printf("Server's new port is : %s\n",token);

//PORT DE DONNEES
                  int port_data = atoi(token);
                  adresse.sin_port= htons(port_data);
                  do {
                  n = recvfrom(server_desc, (char *)buffer,22+6,
                                MSG_WAITALL, ( struct sockaddr *) &adresse,
                                &len);
                  buffer[n] = '\0';
                  printf("Server : %s\n", buffer);
                } while (strcmp(buffer,"FIN") != 0);















  }
}

close(server_desc);
return 0;
}
