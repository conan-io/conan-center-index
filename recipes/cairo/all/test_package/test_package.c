#include <cairo.h>
#include <cairo-version.h>
#include <stdio.h>

int main()
{
    printf("cairo version is %s\n", cairo_version_string());
    return 0;
}
