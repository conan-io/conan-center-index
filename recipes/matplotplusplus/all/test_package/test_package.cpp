#include <matplot/matplot.h>
#include <vector>

int main() {
    auto f = matplot::figure(true); // quiet mode: prevents opening a window
    std::vector<double> x = {1.0, 2.0, 3.0, 4.0};
    std::vector<double> y = {1.0, 4.0, 9.0, 16.0};
    auto p = matplot::plot(x, y);
    p->line_width(2);
    return 0;
}
