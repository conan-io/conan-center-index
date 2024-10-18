#include <SuiteSparse_config.h>

int main() {
    void* x = SuiteSparse_config_malloc(10);
    SuiteSparse_config_free(x);
    return 0;
}
