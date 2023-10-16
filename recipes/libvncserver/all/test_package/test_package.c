#include <stdlib.h>
#include <stdio.h>

#include <rfb/rfbproto.h>
#include <libvncserver/auth.h>


int main(void) {

    unsigned char bytes [CHALLENGESIZE] = {0};
    rfbRandomBytes(&bytes);
    printf("Random bytes: %s\n", bytes);

    return EXIT_SUCCESS;
}

