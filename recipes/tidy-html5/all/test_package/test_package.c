#include <stdio.h>
#include <stdlib.h>
#include <tidy.h>

int main()
{
    printf("tidy-html5 version: %s\n", tidyLibraryVersion());
    return EXIT_SUCCESS;
}
