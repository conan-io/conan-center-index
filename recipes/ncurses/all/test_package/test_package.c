#include <ncurses.h>

#include <stdlib.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("ncurses version '%s'\n", curses_version());
    return EXIT_SUCCESS;
}
