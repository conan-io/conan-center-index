#include <stdio.h>
#include "freexl.h"


int main() {
    const void *handle;
    int ret;
    ret = freexl_open("", &handle);
    freexl_close(handle);

}
