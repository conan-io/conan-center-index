#include <cstdlib>

#include "wildcards.hpp"


int main(void) {
    wildcards::match("Hello, World!", "H*World?");

    return EXIT_SUCCESS;
}
