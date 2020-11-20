#include <stdio.h>
#include "gdk-pixbuf/gdk-pixbuf.h"

int main()
{
    printf("gdk-pixbuf version %s %d.%d.%d\n", gdk_pixbuf_version, gdk_pixbuf_major_version, gdk_pixbuf_minor_version, gdk_pixbuf_micro_version);
    return 0;
}
