#include <sodium.h>
#include <stdio.h>

int main() {
    printf("************* Testing libsodium ***************\n");
    if (sodium_init() == -1) {
        printf("\tFAIL\n");
        return 1;
    }
    printf("\tOK\n");
    printf("***********************************************\n");
    return 0;
}
