#include <iostream>
#include "multi/array.hpp"


int main(void) {
    boost::multi::array<double, 2> multi_array = {
        {1.0, 2.0, 3.0},
        {4.0, 5.0, 6.0},
    };
    std::cout << "Array size: " << multi_array.size() << std::endl;
    return 0;
}
