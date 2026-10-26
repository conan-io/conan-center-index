#include <flashaccept.h>
#include <stdio.h>

/* Link + symbol smoke test: just resolve a flashaccept symbol at runtime. */
int main(void)
{
    printf("flashaccept %s\n", fa_version());
    return 0;
}
