#include "confuse.h"

#include <locale.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "Need at least one argument\n");
        return EXIT_FAILURE;
    }

    cfg_opt_t opts[] =
    {
        CFG_STR("target", "World", CFGF_NONE),
        CFG_END()
    };

    cfg_t *cfg = cfg_init(opts, CFGF_NONE);
    if (cfg_parse(cfg, argv[1]) != CFG_SUCCESS) {
        fprintf(stderr, "cfg_parse failed\n");
        return EXIT_FAILURE;
    }

    char *target = cfg_getstr(cfg, "target");
    printf("Hello, %s!\n", target);

    cfg_free(cfg);
    return EXIT_SUCCESS;
}
