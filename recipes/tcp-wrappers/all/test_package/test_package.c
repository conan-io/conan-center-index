#include "tcpd.h"

#include <stdio.h>

int main (int argc, char *argv[])
{
    struct request_info req;
    request_init(&req, RQ_DAEMON, argv[0], RQ_FILE, 0, 0);
    printf("host_access: %d\n", hosts_access(&req));
    return 0;
}
