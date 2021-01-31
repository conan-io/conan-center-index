#include <backtrace-supported.h>
#include <backtrace.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void
error_callback_create(void* data, const char* msg, int errnum)
{
    fprintf(stderr, "%s", msg);
    if (errnum > 0)
        fprintf(stderr, ": %s", strerror(errnum));
    fprintf(stderr, "\n");
    exit(EXIT_FAILURE);
}

int
main(int argc, char** argv)
{
    void* state;

    state = backtrace_create_state(argv[0], BACKTRACE_SUPPORTS_THREADS,
                                   error_callback_create, NULL);
    backtrace_print(state, 0, stdout);

    return 0;
}
