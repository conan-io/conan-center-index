#include "crypt.h"

#include <stdio.h>
int main()
{
    printf("preferred method: %s\n", crypt_preferred_method());
    return 0;
}
