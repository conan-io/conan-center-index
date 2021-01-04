#include "stringprep.h"

#include <stdio.h>

int main()
{
    printf("Locale charset: %s\n", stringprep_locale_charset());
    return 0;
}
