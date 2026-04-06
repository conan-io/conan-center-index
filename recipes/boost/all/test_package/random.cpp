#include <boost/random.hpp>
#include <iostream>

int main() {
    boost::random::mt19937 rng;
    const auto number = boost::random::uniform_int_distribution<>(1, 100)(rng);
    std::cout << "Testing Boost::Random: " << number << std::endl;
    return 0;
}
