#include <nfd.h>
#include <stdio.h>
#include <stdlib.h>

int main()
{
    const char * error = NFD_GetError();
    printf("last NFD error: \"%s\"\n", error ? error : "(null)");
    return EXIT_SUCCESS;
}
