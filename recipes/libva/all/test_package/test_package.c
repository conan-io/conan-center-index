#include <va/va.h>

#include <stdio.h>

int main()
{
    VADisplay va_display;
    printf("Display is valid: %d", vaDisplayIsValid(0));
    return 0;
}
