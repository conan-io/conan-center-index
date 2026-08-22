#include "smacker.h"

#include <stdio.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Need an argument\n");
        return 1;
    }
    smk obj = smk_open_file(argv[1], 'r');
    if (obj == NULL) {
        printf("Failed to open smk\n");
        return 1;
    }
    smk_close(obj);
    return 0;
}
