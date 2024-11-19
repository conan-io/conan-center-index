#include <stdlib.h>
#include <stdio.h>
#include <keystone/keystone.h>

int main()
{
    unsigned int major = 0, minor = 0;
    ks_version(&major, &minor);
    printf("keystone version %u.%u\n", major, minor);
    return EXIT_SUCCESS;
}
