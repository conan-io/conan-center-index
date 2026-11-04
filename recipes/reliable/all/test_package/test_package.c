#include <reliable.h>
#include <stdio.h>

int main(void)
{
    if (reliable_init() != RELIABLE_OK)
    {
        printf("reliable_init failed\n");
        return 1;
    }
    reliable_term();
    printf("reliable %s\n", RELIABLE_VERSION_FULL);
    return 0;
}
