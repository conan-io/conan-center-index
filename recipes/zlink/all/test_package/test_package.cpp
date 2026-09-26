#include <zlink.h>

int main()
{
    int major = 0;
    int minor = 0;
    int patch = 0;
    zlink_version(&major, &minor, &patch);

    void *context = zlink_ctx_new();
    if (context == nullptr)
        return 1;

    if (zlink_ctx_term(context) != 0)
        return 2;

    return (major > 0 || minor > 0 || patch > 0) ? 0 : 3;
}
