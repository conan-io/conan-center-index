#include <stddef.h>

#include <libdisplay-info/info.h>

int main()
{
    return di_info_parse_edid("", 0) != 0;
}
