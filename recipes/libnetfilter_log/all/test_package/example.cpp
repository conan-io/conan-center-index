#include <iostream>
#include <cstdlib>
#include <libnetfilter_log/libnetfilter_log.h>
#include <libnetfilter_log/libipulog.h>

int main() {
    std::cout << "IPU Log: " << ipulog_strerror(IPULOG_ERR_NONE) << std::endl;

    (void*) nflog_open;
    (void*) nflog_close;

    return EXIT_SUCCESS;
}