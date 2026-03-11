#include "version.hpp"  // tree-gen version
#include <iostream>


int main() {
    std::cout << "tree-gen version: " << get_version() << '\n';
    std::cout << "tree-gen release year: " << get_release_year() << '\n';
}
