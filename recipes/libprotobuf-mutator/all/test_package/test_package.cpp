#include <cstdlib>
#include <iostream>

#include <libprotobuf-mutator/src/mutator.h>


int main() {
    protobuf_mutator::Mutator mutator{};
    mutator.Seed(42);
    return EXIT_SUCCESS;
}
