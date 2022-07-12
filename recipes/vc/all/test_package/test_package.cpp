#include <Vc/Vc>

#include <iostream>

using Vec3D = std::array<Vc::float_v, 3>;

Vc::float_v scalar_product(Vec3D a, Vec3D b) {
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

int main() {
    Vec3D a{1, 2, 3};
    Vec3D b{3, 4, 5};
    std::cout << scalar_product(a, b) << std::endl;
    return 0;
}
