#include <libraw/libraw.h>

int main()
{
    libraw_data_t* libraw_data = libraw_init(0);

    libraw_close(libraw_data);

    return 0;
}
