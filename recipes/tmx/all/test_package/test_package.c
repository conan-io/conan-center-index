#include <tmx.h>

#include <stdio.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Need at least one argument\n");
        return 1;
    }

    tmx_map *map = tmx_load(argv[1]);
    if (map == NULL) {
        tmx_perror("Cannot load map");
        return 1;
    }
    tmx_map_free(map);

    return 0;
}
