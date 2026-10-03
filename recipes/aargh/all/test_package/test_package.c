#include <stdio.h>

#define ARGH_IMPLEMENTATION
#include "argh.h"

int main(int argc, char **argv)
{
    int jobs = 1;
    argh_parser p;
    argh_init(&p, "test_package", NULL);
    argh_int(&p, 'j', "jobs", &jobs, "Parallel jobs");
    if (!argh_parse(&p, argc, argv))
        return argh_exit_code(&p);
    printf("aargh %s: jobs=%d\n", ARGH_VERSION, jobs);
    return 0;
}
