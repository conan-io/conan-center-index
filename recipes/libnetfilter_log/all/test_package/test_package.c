#include <stdio.h>
#include <stdlib.h>
#include <libnetfilter_log/libnetfilter_log.h>
#include <libnetfilter_log/libipulog.h>

int main() {
    printf("IPU Log: %s\n", ipulog_strerror(IPULOG_ERR_NONE));

    (void*) nflog_open;
    (void*) nflog_close;

    return EXIT_SUCCESS;
}