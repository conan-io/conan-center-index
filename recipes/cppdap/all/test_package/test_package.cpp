#include <cstdlib>
#include "dap/dap.h"

int main() {

    dap::initialize();
    dap::terminate();

    return EXIT_SUCCESS;
}
