#include <stdlib.h>
#include "objc/objc.h"
#include "objc/encoding.h"
#include <stdio.h>

int main(void) {
    char type = _C_CLASS;
    objc_sizeof_type(&type);
    printf("libobjc2 test package successful!\n");
    return EXIT_SUCCESS;
}
