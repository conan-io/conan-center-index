#include <bx/string.h>

int main()
{
    char tmp[1024];
    prettify(tmp, BX_COUNTOF(tmp), 4000, bx::Units::Kilo);
}
