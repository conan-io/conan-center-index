#include <libyang/libyang.h>

int main()
{
    struct ly_ctx *ctx = NULL;
    if ( ly_ctx_new( NULL, 0, &ctx ) )
    {
        return 1;
    }
    return 0;
}
