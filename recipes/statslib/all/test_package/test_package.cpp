#include "stats.hpp"

int main()
{
    constexpr double dens_1 = stats::dlaplace(1.0, 1.0, 2.0);  // answer = 0.25
    constexpr double prob_1 = stats::plaplace(1.0, 1.0, 2.0);  // answer = 0.5
    constexpr double quant_1 = stats::qlaplace(0.1, 1.0, 2.0); // answer = -2.218875...

    return 0;
}
