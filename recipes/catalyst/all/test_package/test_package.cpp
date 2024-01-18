#include <cstdlib>
#include <catalyst.hpp>
#include <conduit.h>

int main(void) {
    conduit_cpp::Node node;
    const auto init{catalyst_initialize(conduit_cpp::c_node(&node))};
    const auto exec{catalyst_execute(conduit_cpp::c_node(&node))};
    const auto finalize{catalyst_finalize(conduit_cpp::c_node(&node))};
    return EXIT_SUCCESS;
}
