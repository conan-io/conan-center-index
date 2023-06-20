#include "X11/Xft/Xft.h"

#include <stdio.h>
int main()
{
    if(!XftInit(""))
        printf("Could not init Xft\n");
    printf("Xft version: %d\n", XftGetVersion());
    return 0;
}
