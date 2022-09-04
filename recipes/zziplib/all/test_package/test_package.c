#include <zzip/zzip.h>
#include <zzip/plugin.h>

#include <stdio.h>

int main()
{
    zzip_plugin_io_t plugin = zzip_get_default_io();

    printf("zzip code 0 means %s\n", zzip_strerror(0));
    return plugin == 0;
}
