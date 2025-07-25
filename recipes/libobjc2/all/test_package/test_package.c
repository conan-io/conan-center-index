#include <stdlib.h>
#include "objc/objc.h"
#include "objc/encoding.h"

int main(void) {
    char type = _C_CLASS;
    objc_sizeof_type(&type);
    return EXIT_SUCCESS;
}
