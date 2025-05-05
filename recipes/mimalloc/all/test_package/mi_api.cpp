#include "mimalloc.h"

#include <iostream>
#include <vector>

int main() {
    std::vector<int, mi_stl_allocator<int>> vec;
    vec.push_back(1);
    vec.pop_back();

    std::cout << "mimalloc version " << mi_version() << "\n";
    return 0;
}
