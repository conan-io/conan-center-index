#include <stdlib.h>
#include "libbigwig/bigWig.h"


int main(void) {
    bigWigFile_t *fp = NULL;

    bwInit(1<<17);
    fp = bwOpen("test_package.bw", NULL, "w");
    bwCreateHdr(fp, 10);
    bwClose(fp);
    bwCleanup();

    return EXIT_SUCCESS;
}
