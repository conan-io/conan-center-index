#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "readline/readline.h"
#include "readline/history.h"

/*
 * libreadline already contains the history library, and libhistory is a second,
 * complete copy with its own state. If libhistory is linked BEFORE libreadline
 * (cpp_info.libs = ["history", "readline"]), on macOS the application's
 * add_history() fills libhistory's list while readline's own previous-history
 * (up-arrow / Ctrl-P) reads libreadline's list, which stays empty.
 *
 * Add one entry, feed readline() the keys "Ctrl-P, Enter" and check that the
 * entry is recalled.
 */
static int check_history(void) {
    FILE *in = tmpfile();
    FILE *out = fopen("/dev/null", "w");
    if (!in || !out) {
        return 0;
    }
    fputs("\x10\n", in);
    rewind(in);

    setenv("TERM", "dumb", 1);
    rl_instream = in;
    rl_outstream = out;
    rl_variable_bind("enable-bracketed-paste", "off");
    rl_variable_bind("editing-mode", "emacs");

    using_history();
    add_history("conan-center-index");

    char *line = readline("");
    int recalled = line && strcmp(line, "conan-center-index") == 0;
    if (!recalled) {
        fprintf(stderr, "history not recalled by readline (got \"%s\")\n", line ? line : "(null)");
    }
    free(line);
    return recalled;
}

int main(int argc, char *argv[]) {

    if(!ISALPHA('a') || !ISDIGIT('1')) {
        return EXIT_FAILURE;
    }
    rl_message("conan-center-index");

    if (!check_history()) {
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
