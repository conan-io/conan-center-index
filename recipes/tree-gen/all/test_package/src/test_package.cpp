#include "directory.hpp"  // the generated file
#include "utils.hpp"
#include "version.hpp"  // tree-gen version

#include <cstdio>
#include <iostream>
#include <sstream>  // ostringstream
#include <stdexcept>


void print_tree_gen_version() {
    std::printf("tree-gen version: %s\n", TREE_GEN_VERSION);
    std::printf("tree-gen release year: %s\n", TREE_GEN_RELEASE_YEAR);
}

int main() {
    print_tree_gen_version();

    auto system = tree::base::make<directory::System>();
    ASSERT(!system.is_well_formed());
}
