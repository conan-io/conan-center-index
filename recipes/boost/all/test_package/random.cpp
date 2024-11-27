#include <boost/random.hpp>

int main() {
    boost::random::mt19937 rng;
    boost::random::uniform_int_distribution<>(1, 100)(rng);
    return 0;
}
