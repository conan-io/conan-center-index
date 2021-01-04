#include "matio.h"

#include <stdio.h>

int main()
{
    int major, minor, release;
    Mat_GetLibraryVersion(&major, &minor, &release);
    printf("Test application successfully ran using matio %d.%d.%d!\n", major, minor, release);
    return 0;
}
