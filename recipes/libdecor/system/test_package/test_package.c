#include <libdecor.h>

int main(void)
{
    volatile void *fn = (void *)&libdecor_new;
    (void)fn;
    return 0;
}
