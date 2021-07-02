#include <search.h>

#include <stdio.h>

static void walk_tree(const void *what, VISIT kind, int level) {
}

int main() {
    void *root = NULL;
    twalk(root, walk_tree);
    return 0;
}
