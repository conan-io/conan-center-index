#include <bsplinebasis1d.h>
#include <vector>

int main() {
    std::vector<double> knots = {1, 1, 1, 2.1, 3.1, 4, 4, 4};
    SPLINTER::BSplineBasis1D bb(knots, 2);
}
