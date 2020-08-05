#include "xkbcommon/xkbcommon.h"

int main()
{
    struct xkb_context *ctx = xkb_context_new(XKB_CONTEXT_NO_FLAGS);
    if (!ctx) return 1;
    return 0;
}
