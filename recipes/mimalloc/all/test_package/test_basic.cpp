#include "mimalloc.h"

#include <iostream>

int main() {
    int *data = new int(1337);
    delete data;

    std::cout << "mimalloc version " << mi_version() << "\n";
    mi_stats_print(0);
    return 0;
}
