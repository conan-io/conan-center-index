#include <stdio.h>

#include "xls.h"

int main() {
    struct xlsWorkBook*  wb;
    struct xlsWorkSheet* ws;

    printf("libxls version : %s\n", xls_getVersion());

    return 0;
}
