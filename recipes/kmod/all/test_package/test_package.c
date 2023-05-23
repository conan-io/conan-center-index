#include <stdlib.h>
#include <stdio.h>
#include "libkmod.h"

int main(int argc, char * argv[])
{
    struct kmod_ctx *ctx = kmod_new(NULL, NULL);
    if (ctx)
    {
        struct kmod_list * list, * mod;
        if (kmod_module_new_from_loaded(ctx, &list) >= 0)
        {
            kmod_list_foreach(mod, list)
            {
                struct kmod_module *kmod = kmod_module_get_module(mod);
                printf("%s\n", kmod_module_get_name(kmod));
            }
	    kmod_module_unref_list(list);
        }
        kmod_unref(ctx);
    }
    return EXIT_SUCCESS;
}
