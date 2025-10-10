#include <libmem/libmem.h>
#include <stdio.h>

int main(void) {
    lm_thread_t resultThread;
    lm_bool_t result = LM_GetThread(&resultThread);
    if (result == LM_TRUE) {
        printf("libmem C API test: Successfully got current thread\n");
    }
    return 0;
}
