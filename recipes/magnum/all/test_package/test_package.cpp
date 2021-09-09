#include <iostream>
#include "Magnum/Math/Vector.h"
#include "Magnum/Math/StrictWeakOrdering.h"

/*
    I would like to use some windowless application to test, like
    https://github.com/mosra/magnum-bootstrap/tree/windowless
    but it doesn't work in CI, it complains about EGL_NOT_INITIALIZED
    (headless machine?)
*/

int main() {
    const Magnum::Math::Vector<2, Magnum::Float> v2a{1.0f, 2.0f};
    const Magnum::Math::Vector<2, Magnum::Float> v2b{2.0f, 3.0f};
    const Magnum::Math::Vector<2, Magnum::Float> v2c{1.0f, 3.0f};

    Magnum::Math::StrictWeakOrdering o;
    if (o(v2a, v2b)) {
        std::cout << "Magnum working\n";
    }
}
