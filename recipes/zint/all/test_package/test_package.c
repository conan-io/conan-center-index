#include "zint.h"

#include <stdio.h>

int main(void) {
    struct zint_symbol *symbol = ZBarcode_Create();
    int error = ZBarcode_Encode(symbol, (unsigned char *)"Hello", 0);
    ZBarcode_Delete(symbol);

    printf("Zint version: %d\n", ZBarcode_Version());
    return error < ZINT_WARN_INVALID_OPTION ? 0 : 1;
}
