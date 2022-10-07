#include <stdio.h>
#include <ghostscript/iapi.h>

int main(void) {
    gsapi_revision_t r;
    gsapi_revision(&r, sizeof(r));
    printf("gsapi_revision: %i\n", r.revision);
    printf("gsapi_revisiondate: %i\n", r.revisiondate);
}
