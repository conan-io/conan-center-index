#include "directory.hpp"  // the generated file
#include "utils.hpp"
#include "version.hpp"  // tree-gen version

#include <iostream>


void print_tree_gen_version() {
    std::cout << "tree-gen version: " << get_version() << "\n";
    std::cout << "tree-gen release year: " << get_release_year() << "\n";
}

int main() {
    print_tree_gen_version();

    auto system = tree::base::make<directory::System>();
    ASSERT(!system.is_well_formed());
}
