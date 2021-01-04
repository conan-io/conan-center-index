#include "curses.h"

#include <stdlib.h>
#include <stdio.h>

int main()
{
    printf("PDCurses version %s\n", curses_version());
    return EXIT_SUCCESS;
}
