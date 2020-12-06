#include <ev.h>
#include <stdio.h>

int main()
{
    printf("libev ver=%d.%d\n", ev_version_major(), ev_version_minor());
    return 0;
}
