#include <matplotlibcpp.h>

#include <cmath>
#include <vector>

namespace plt = matplotlibcpp;

int main()
{
    // u and v are respectively the x and y components of the arrows we're plotting
    std::vector<int> x, y, u, v;
    for (int i = -5; i <= 5; i++) {
        for (int j = -5; j <= 5; j++) {
            x.push_back(i);
            u.push_back(-i);
            y.push_back(j);
            v.push_back(-j);
        }
    }
    plt::quiver(x, y, u, v);
    plt::save("test.png");

    // The interpreter segfaults if it is not shut down explicitly
    // https://github.com/lava/matplotlib-cpp/issues/248
    plt::detail::_interpreter::kill();
}
