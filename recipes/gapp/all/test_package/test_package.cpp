#include "gapp/gapp.hpp"
#include <iostream>

int main() {
    std::cout << "random number: " << gapp::rng::randomInt(0, 10) << "\n";
}
