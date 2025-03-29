#include "tslib.h"
#include <stddef.h>

int main()
{
    struct tsdev *ts;
    ts = ts_setup(NULL, 0);
    return ts != NULL;
}
