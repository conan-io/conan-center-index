#include <stdlib.h>
#include <stdio.h>
#include <keystone/keystone.h>

int main()
{
    int major = 0, minor = 0;
    ks_version(&major, &minor);
    printf("keystone version %d.%d\n", major, minor);
    return EXIT_SUCCESS;
}
