#include <noise/noisegen.h>

#include <iostream>

int main() {
    std::cout << noise::IntValueNoise3D(4, 2, 5) << std::endl;
    return 0;
}
