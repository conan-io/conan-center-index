#include <sys/types.h>
#include "nfsc/libnfs.h"

int main() {
    struct nfs_context* nfs = nfs_init_context();
    
    if (nfs == NULL) {
        return 0;
    }
    nfs_destroy_context(nfs);
    return 0;
}
