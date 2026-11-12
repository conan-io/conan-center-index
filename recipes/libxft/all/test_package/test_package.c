#include "X11/Xft/Xft.h"

#include <stdio.h>
int main()
{
    printf("Xft version: %d\n", XftGetVersion());
    return 0;
}
