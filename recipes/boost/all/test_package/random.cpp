#include <boost/random.hpp>
#include <iostream>

int main() {
    BOOST_NAMESPACE::random::mt19937 rng;
    const auto number = BOOST_NAMESPACE::random::uniform_int_distribution<>(1, 100)(rng);
    std::cout << "Testing Boost::Random: " << number << std::endl;
    return 0;
}
