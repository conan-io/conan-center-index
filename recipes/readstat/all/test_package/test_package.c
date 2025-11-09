#include <stdio.h>
#include <stdlib.h>
#include "readstat.h"

int main() {

    readstat_error_t error = READSTAT_OK;
    readstat_parser_t *parser = readstat_parser_init();

    printf("Build test sucess\n");
    return 0;
}