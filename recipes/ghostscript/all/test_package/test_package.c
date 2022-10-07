#include <stdio.h>
#include <ghostscript/iapi.h>

int main(void) {
    gsapi_revision_t r;
    printf("gsapi_revision: %i", gsapi_revision(&r, sizeof(r)).revision);
}
