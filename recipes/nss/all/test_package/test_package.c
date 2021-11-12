#include "nss.h"
#include <stdio.h>

int main() {
    SECStatus rv;
    printf("NSS version: %s\n", NSS_GetVersion());

    rv = NSS_NoDB_Init("./tmp");
    if (rv != SECSuccess){
        printf("NSS_Init failed in directory tmp\n");
        return 1;
    }

    return 0;
}
