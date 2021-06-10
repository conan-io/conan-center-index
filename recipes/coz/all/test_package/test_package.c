#include <coz.h>
#include <stdio.h>

int
main(int argc, char **argv)
{
    COZ_PROGRESS_NAMED("something");
    printf("Hello, Coz!\n");

    return 0;
}
