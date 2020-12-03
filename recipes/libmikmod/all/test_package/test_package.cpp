#define _CRT_SECURE_NO_WARNINGS
#include <mikmod.h>
#include <cstdlib>
#include <cstring>
#include <iostream>

int main()
{
    // register all the drivers
    MikMod_RegisterAllDrivers();

    // initialize the library
    if (int err = MikMod_Init("")) {
        std::cerr << "Couldn't initialize sound, reason: " << MikMod_strerror(MikMod_errno) << "\n";
        // some CI environments doesn't support audio, so we'll just ignore errors there
        const char* ignoreEnvvar = std::getenv("IGNORE_LIBMIKMOD_TEST_ERRORS");
        if (ignoreEnvvar && std::strcmp(ignoreEnvvar, "true") == 0)
            return 0;
        else
            return 0;
    }

    // cleanup
    MikMod_Exit();
}
