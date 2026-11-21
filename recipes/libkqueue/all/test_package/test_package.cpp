#include <cstdlib>
#include <stdio.h>
#include "kqueue/sys/event.h"

int main() {
    int kqfd = kqueue();
    if (kqfd < 0) {
        perror("kqueue");
        return EXIT_FAILURE;
    }

    struct kevent kev, receipt;
    EV_SET(&kev, 0, EVFILT_LIBKQUEUE, EV_ADD, NOTE_VERSION_STR, 0, NULL);
    struct timespec timeout = {0, 0};
    if (kevent(kqfd, &kev, 1, &receipt, 1, &timeout) != 1) {
        perror("kevent");
        return EXIT_FAILURE;
    }

    printf("libkqueue version - %s\n", (char *)receipt.udata);

    return EXIT_SUCCESS;
}
