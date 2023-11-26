#include "multi/array.hpp"

namespace multi = boost::multi;

int main(void) {
    multi::array<int, 2> arr({10, 20}, 99);

    std::cout << "should print 99: " << arr[2][3] << std::endl;
}
