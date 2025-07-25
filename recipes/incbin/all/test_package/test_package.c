#include <incbin.h>
#include <stdio.h>

#if INCBIN_ALIGNMENT == 0
#error "INCBIN_ALIGNMENT must be non-zero"
#endif

int main(void)
{
    printf("INCBIN_ALIGNMENT=%d\n", INCBIN_ALIGNMENT);
    return 0;
}
