#include <stdio.h>
#include "ccmap.h"
#include "cclist.h"
#include "ccheap.h"
#include "ccvector.h"

int main(void) {
    ccmap_t     m;
    cclist_t    l;
    ccheap_t    h;
    ccvector_t  v;

    /* Verify headers are accessible and basic init compiles */
    ccmap_init(&m, NULL);
    cclist_init(&l);
    (void)heap_init(&h, NULL);
    (void)ccvector_init(&v);

    printf("ccalg headers OK\n");
    return 0;
}
