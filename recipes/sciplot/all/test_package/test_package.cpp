#include <sciplot/sciplot.hpp>
#include <iostream>
#include <vector>

int main() {
    std::vector<double> x = {0.0, 1.0, 2.0};
    std::vector<double> y = {0.0, 1.0, 4.0};
    sciplot::Plot2D plot;
    plot.xlabel("x");
    plot.drawCurve(x, y);
    std::cout << "sciplot test_package OK\n";
    return 0;
}
