#include "zint.h"

#include <stdio.h>

#define ZINT_MAJOR(V) (((V)/10000) % 100)
#define ZINT_MINOR(V) (((V)/  100) % 100)
#define ZINT_PATCH(V) (((V)      ) % 100)


int main() {
    int version = ZBarcode_Version();
    printf("Zint version: %d.%d.%d\n", ZINT_MAJOR(version), ZINT_MINOR(version), ZINT_PATCH(version));

    struct zint_symbol *sym = ZBarcode_Create();
    if (!sym) {
        fprintf(stderr, "ZBarcode_Create failed\n");
        return 1;
    }
    sym->symbology = BARCODE_CODE128;
    int ret = ZBarcode_Encode(sym, (const unsigned char *)"conan-zint-test", 0);
    if (ret != 0) {
        fprintf(stderr, "ZBarcode_Encode failed: %s\n", sym->errtxt);
        ZBarcode_Delete(sym);
        return 1;
    }
    printf("Encoded %d rows x %d cols\n", sym->rows, sym->width);
    ZBarcode_Delete(sym);
    return 0;
}
