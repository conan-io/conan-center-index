#include "apr_version.h"

#include <stdio.h>

int main() {
    printf("APR version %s\n", apr_version_string());
    return 0;
}
