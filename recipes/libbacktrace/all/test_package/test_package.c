#include <backtrace-supported.h>
#include <backtrace.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void
error_callback(void* data, const char* msg, int errnum)
{
    fprintf(stderr, "%s", msg);
    if (errnum > 0)
        fprintf(stderr, ": %s", strerror(errnum));
    fprintf(stderr, "\n");
    exit(EXIT_FAILURE);
}

int
simple_callback(void* data, uintptr_t pc)
{
    printf("0x%016lu\n", pc);
    return 0;
}

int
main(int argc, char** argv)
{
    void* state;

    state = backtrace_create_state(argv[0], BACKTRACE_SUPPORTS_THREADS, error_callback, NULL);
    printf("Simple backtrace:\n");
    backtrace_simple(state, 0, simple_callback, error_callback, NULL);

    return 0;
}
