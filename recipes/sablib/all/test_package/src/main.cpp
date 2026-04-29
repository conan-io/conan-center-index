#include <vector>
#include "sablib/sablib.h"

int main()
{
    std::vector<double> signal = {1.0, 2.0, 3.0, 2.0, 1.0};
    auto result = sablib::Whittaker(signal, 1.0, 2);
    return 0;
}
