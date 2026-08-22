#define _CRT_SECURE_NO_WARNINGS
#include <mikmod.h>
#include <stdio.h>

int main()
{
    int err;
    // register all the drivers
    MikMod_RegisterAllDrivers();

    // initialize the library
    if (err = MikMod_Init("")) {
        printf("Couldn't initialize sound, error %d, reason: %s\n", err, MikMod_strerror(MikMod_errno));
        return 0;
    }

    // cleanup
    MikMod_Exit();
    return 0;
}
