#include <oping.h>
#include <stdio.h>

int main() {
    printf("************* Testing liboping ***************\n");
    pingobj_t *po;
    po = ping_construct();
    if (po == NULL) {
        printf("\tFAIL\n");
        return 1;
    }
    ping_destroy(po);
    printf("\tOK\n");
    printf("***********************************************\n");
    return 0;
}
