#include <ncurses.h>

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#if defined(_WINDOWS)
#include <windows.h>
#else
#include <unistd.h>
#endif

int main(int argc, char *argv[]) {
    WINDOW* window = NULL;

    printf("ncurses version: %s\n", curses_version());

    window = initscr();

    if (window != NULL) {
        if (start_color() != ERR) {
            init_pair(1, COLOR_BLACK, COLOR_CYAN);
            init_pair(2, COLOR_BLACK, COLOR_GREEN);

            attron(COLOR_PAIR(1));
            printw("Conan, the C / C++ Package Manager for Developers\n");
            attron(COLOR_PAIR(2));
        }
        printw("This is the ncurses Conan package!\n");

        wrefresh(stdscr);
#ifdef _MSC_VER
        Sleep(1000);
#else
        sleep(1);
#endif
    }
    endwin();
    return EXIT_SUCCESS;
}
