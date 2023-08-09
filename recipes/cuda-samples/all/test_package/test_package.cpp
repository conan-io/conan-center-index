#include <cstdlib>
#include <iostream>
#include <cmath>

#include "nvVector.h"
#include "nvMatrix.h"
#include "nvQuaternion.h"


int main() {
    auto q = normalize(nv::quaternion<float>(0, 0, 0, 4));

    std::cout << "Normalized nv::quaternion(): " << q[0] << ", " << q[1] << ", " << q[2] << ", " << q[3] << std::endl;

    return EXIT_SUCCESS;
}
