#include "utf8proc.h"

#include <stdio.h>

int main()
{
    printf("utf8proc version %s\n", utf8proc_version());
    printf("unicode version %s\n", utf8proc_unicode_version());
    return 0;
}
