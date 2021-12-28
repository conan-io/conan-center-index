#include <stdio.h>
#include <stdlib.h>
#include <libkmod.h>

int main(int argc, char **argv)
{
    struct kmod_ctx *my_ctx = kmod_new(NULL, NULL);;
    if (my_ctx == NULL) {
        perror("Cannot create kmod context");
    }

    struct kmod_module *my_module;
    if (kmod_module_new_from_name(my_ctx, "regmap", &my_module)) {
        perror("Cannot create regmap module");
    } else {
        printf("Successfully created regmap module\n");
        kmod_module_unref(my_module);
    }

    kmod_unref(my_ctx);
    return EXIT_SUCCESS;
}
