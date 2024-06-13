#include <stdio.h>
#include <stdlib.h>
#include "popt.h"


int main(int argc, const char* argv[]) {
    struct poptOption table[] = {
        POPT_AUTOHELP
        POPT_TABLEEND
    };

    poptContext context = poptGetContext(NULL, argc, argv, table, 0);
    poptGetNextOpt(context);
    poptFreeContext(context);

    return EXIT_SUCCESS;
}
