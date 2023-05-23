#include <plf_nanotimer.h>

#include <iostream>

int main() {
    plf::nanotimer timer;
    timer.start();
    double results = timer.get_elapsed_ns();
    std::cout << "Timing: " << results << " nanoseconds." << std::endl;
    return 0;
}
