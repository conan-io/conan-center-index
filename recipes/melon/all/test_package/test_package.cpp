#include <cstdlib>
#include <iostream>

#include "melon/container/static_digraph.hpp"
#include "melon/utility/static_digraph_builder.hpp"
#include "melon/version.hpp"


int main(void) {
    melon::static_digraph_builder<melon::static_digraph, int> builder(6);
    std::cout << "Melon version: " << MELON_VERSION << std::endl;
    return EXIT_SUCCESS;
}
