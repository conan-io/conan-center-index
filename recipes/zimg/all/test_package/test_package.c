#include <zimg.h>
#include <stdio.h>

int main()
{
    unsigned major, minor;
    zimg_get_api_version(&major, &minor);
    printf("zimg version: %u.%u\n", major, minor);
    return 0;
}
