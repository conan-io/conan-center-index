#include <iostream>
#include "sole.hpp"

int main() {
    sole::uuid u0 = sole::uuid0(), u1 = sole::uuid1(), u4 = sole::uuid4();

    std::cout << "uuid v0 string : " << u0 << std::endl;
    std::cout << "uuid v0 base62 : " << u0.base62() << std::endl;
    std::cout << "uuid v0 pretty : " << u0.pretty() << std::endl << std::endl;

    std::cout << "uuid v1 string : " << u1 << std::endl;
    std::cout << "uuid v1 base62 : " << u1.base62() << std::endl;
    std::cout << "uuid v1 pretty : " << u1.pretty() << std::endl << std::endl;

    std::cout << "uuid v4 string : " << u4 << std::endl;
    std::cout << "uuid v4 base62 : " << u4.base62() << std::endl;
    std::cout << "uuid v4 pretty : " << u4.pretty() << std::endl << std::endl;

    u1 = sole::rebuild("F81D4FAE-7DEC-11D0-A765-00A0C91E6BF6");
    std::cout << "uuid v1 rebuilt: " << u1 << " -> " << u1.pretty()
              << std::endl;

    u4 = sole::rebuild("GITheR4tLlg-BagIW20DGja");
    std::cout << "uuid v4 rebuilt: " << u4 << " -> " << u4.pretty()
              << std::endl;
}
