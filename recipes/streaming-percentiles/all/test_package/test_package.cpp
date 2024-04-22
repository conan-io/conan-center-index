#include <cstdlib>
#include <iostream>

#include "stmpct/gk.hpp"
int main(int argc, char* argv[]) {
    double epsilon = 0.1;
    stmpct::gk<double> g(epsilon);
    for (int i = 0; i < 1000; ++i)
        g.insert(rand());
    double p50 = g.quantile(0.5); // Approx. median
    double p95 = g.quantile(0.95); // Approx. 95th percentile

    std::cout << "median : " << p50 << " 95th percentile : " << p95 << std::endl;

    return 0;
}
