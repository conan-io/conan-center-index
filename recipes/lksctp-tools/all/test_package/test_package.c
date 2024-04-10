#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <netinet/in.h>
#include <netinet/sctp.h>

int main() {
    int sockfd;

    sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
    close(sockfd);

    return 0;
}
