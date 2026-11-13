#include <cstdlib>
#include <iostream>

#include "icey.h"
#include "icy/datetime.h"

int main() {
    icy::Stopwatch stopwatch;
    stopwatch.reset();
    std::cout << "Icey Test package: " << stopwatch.elapsedSeconds() << std::endl;
    return EXIT_SUCCESS;
}
