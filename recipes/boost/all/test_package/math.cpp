#include <iostream>
#include <boost/math/tr1.hpp>

int main() {
    const auto result = boost::math::tr1::boost_lgammal(1.0L) == 0.0L ? 0 : 1;
    std::cout << "Boost.Math test result: " << result << std::endl;
    return 0;
}