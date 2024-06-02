#include <cstdlib>

#include <libprotobuf-mutator/src/mutator.h>


int main() {
    protobuf_mutator::Mutator mutator{};
    const auto seed_value{42};
    mutator.Seed(seed_value);
    return EXIT_SUCCESS;
}
