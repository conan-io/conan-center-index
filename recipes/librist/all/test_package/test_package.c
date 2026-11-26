#include <librist/librist.h>

#include <stdio.h>

int main(void)
{
    printf("librist version %s, API %s\n", librist_version(), librist_api_version());
    return 0;
}
