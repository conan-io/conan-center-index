#include <stddef.h>

#include <libdis.h>

int main()
{
    x86_init(opt_none, NULL, NULL);
    x86_cleanup();
    return 0;
}
