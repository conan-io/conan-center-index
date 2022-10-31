#include <matplot/matplot.h>

#include <cmath>
#include <vector>

int main()
{
    std::vector<double> x = matplot::linspace(0, 2 * matplot::pi);
    std::vector<double> y = matplot::transform(x, [](auto x) { return std::sin(x); });
    return 0;
}
