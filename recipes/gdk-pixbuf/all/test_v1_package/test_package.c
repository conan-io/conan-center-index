#include <stdio.h>
#include "gdk-pixbuf/gdk-pixbuf.h"

int main()
{
    GdkPixbuf *pixbuf;
    printf("gdk-pixbuf version %s %d.%d.%d\n", gdk_pixbuf_version, gdk_pixbuf_major_version, gdk_pixbuf_minor_version, gdk_pixbuf_micro_version);
    pixbuf = gdk_pixbuf_new(GDK_COLORSPACE_RGB, TRUE, 8, 100, 100);

    g_assert (gdk_pixbuf_get_colorspace (pixbuf) == GDK_COLORSPACE_RGB);
    g_assert (gdk_pixbuf_get_bits_per_sample (pixbuf) == 8);
    g_assert (gdk_pixbuf_get_has_alpha (pixbuf));
    g_assert (gdk_pixbuf_get_n_channels (pixbuf) == 4);

    g_assert (gdk_pixbuf_get_width (pixbuf) == 100);
    g_assert (gdk_pixbuf_get_height (pixbuf) == 100);

    g_object_unref(pixbuf);
    return 0;
}
