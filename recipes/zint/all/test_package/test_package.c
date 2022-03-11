#include "zint.h"

#include <stdio.h>

#define ZINT_MAJOR(V) (((V)/10000) % 100)
#define ZINT_MINOR(V) (((V)/  100) % 100)
#define ZINT_PATCH(V) (((V)      ) % 100)


int main() {
    struct zint_symbol *zbar = ZBarcode_Create();
    ZBarcode_Delete(zbar);

    int version = ZBarcode_Version();
    printf("Zint version: %d.%d.%d\n", ZINT_MAJOR(version), ZINT_MINOR(version), ZINT_PATCH(version));
}
