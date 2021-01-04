#include <stdlib.h>
#include <stdio.h>

#include <getopt.h>

int main(int argc, char * argv[])
{
    int option_index = 0;
    int c = getopt(argc, argv, "v");
    switch (c) {
        case -1:
            puts("No more options");
            break;
        case 'v':
            puts("version : 1");
            break;
        default:
            puts("no option found");
    }
    return EXIT_SUCCESS;
}
