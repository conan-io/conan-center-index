#include <stdlib.h>
#include <stdio.h>
#include <capstone/capstone.h>

int main()
{
    int major = 0, minor = 0;
    cs_version(&major, &minor);
    printf("capstone version %d.%d\n", major, minor);
    return EXIT_SUCCESS;
}
