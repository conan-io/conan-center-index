#include "idn2.h"

#include <stdio.h>
#include <stdlib.h>

int main()
{
    char *output = NULL;
    int rc = idn2_to_ascii_lz("conan.io", &output, IDN2_TRANSITIONAL |IDN2_NFC_INPUT);

    printf("returned: %s\n", output);
    printf("strerror: %s\n", idn2_strerror(rc));
    idn2_free(output);

    if (rc != IDN2_OK) {
        return 1;
    }

    return 0;
}
